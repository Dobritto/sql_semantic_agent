from agent.graph import build_graph
from agent.schemas import (
    RouterResult,
    SQLToolParams,
    DecompositionResult,
    SubTask,
)
from tests.conftest import StubRouter, StubDecomposer, StubSemanticIndex, StubLLMClient, StubDBClient


def _base_state(question: str) -> dict:
    """Полный стартовый state со всеми полями AgentState — вынесено
    в helper, чтобы не дублировать один и тот же большой словарь
    в каждом тесте этого файла."""
    return {
        "question": question,
        "route": None,
        "final_answer": None,
        "decomposition_result": None,
        "subtask_index": 0,
        "current_sql": None,
        "current_prompt": None,
        "sql_error": None,
        "attempt": 0,
        "sql_columns": None,
        "sql_rows": None,
        "subtask_results": []
    }


def _build_test_graph(db: StubDBClient):
    route_result = RouterResult(
        tool="sql_tool",
        params=SQLToolParams(question="сколько активных пользователей за 2022 год"),
        reasoning="аналитический вопрос",
    )
    decomposition_result = DecompositionResult(
        is_complex=False,
        reasoning="один простой вопрос",
        subtasks=[
            SubTask(
                question="сколько активных пользователей за 2022 год",
                metric_id="active_users",
                date_from="2022-01-01",
                date_to="2023-01-01",
            )
        ],
    )
    fake_config = {
        "db_schema": "тестовая схема БД",
        "metrics": {
            "active_users": {
                "label": "Активные пользователи",
                "description": "тест",
                "sql": "COUNT(DISTINCT ue.user_id)",
                "requires_tables": ["userentry"],
                "filter": None,
            }
        },
        "dimensions": {},
    }

    return build_graph(
        StubRouter(route_result),
        StubDecomposer(decomposition_result),
        available_metrics=["active_users"],
        si=StubSemanticIndex(dimensions=[], config=fake_config),
        llm=StubLLMClient(response="```sql\nSELECT COUNT(*) FROM userentry\n```"),
        db=db,
    )


def test_execute_sql_retries_then_succeeds():
    db = StubDBClient([
        (False, 'column "foo" does not exist', None),  # первая попытка — ошибка
        (True, ["count"], [(42,)]),                      # вторая попытка — успех
    ])
    graph = _build_test_graph(db)

    final_state = graph.invoke(_base_state("сколько активных пользователей за 2022 год"))

    assert final_state["attempt"] == 0  # сброшен record_subtask_result-ом после успеха
    assert len(final_state["subtask_results"]) == 1
    assert final_state["subtask_results"][0]["rows"] == [(42,)]
    assert final_state["final_answer"] is not None


def test_execute_sql_gives_up_after_max_attempts():
    db = StubDBClient([
        (False, "синтаксическая ошибка", None),  # всегда падает
    ])
    graph = _build_test_graph(db)

    final_state = graph.invoke(_base_state("сколько активных пользователей за 2022 год"))

    assert final_state["attempt"] == 3
    assert final_state["sql_error"] is not None
    assert "Не удалось" in final_state["final_answer"]