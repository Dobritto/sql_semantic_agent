from agent.graph import build_graph
from agent.schemas import (
    RouterResult,
    SQLToolParams,
    DecompositionResult,
    SubTask,
)
from tests.conftest import StubRouter, StubDecomposer, StubSemanticIndex, StubLLMClient, StubDBClient


def test_graph_generates_sql_for_single_subtask():
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

    graph = build_graph(
        StubRouter(route_result),
        StubDecomposer(decomposition_result),
        available_metrics=["active_users"],
        si=StubSemanticIndex(dimensions=[], config=fake_config),
        llm=StubLLMClient(response="```sql\nSELECT COUNT(*) FROM userentry\n```"),
        db=StubDBClient([(True, ["count"], [(42,)])]),
    )

    final_state = graph.invoke({
        "question": "сколько активных пользователей за 2022 год",
        "route": None,
        "final_answer": None,
        "decomposition_result": None,
        "subtask_index": 0,
        "current_sql": None,
        "subtask_results": []
    })

    assert final_state["subtask_results"][0]["sql"] == "SELECT COUNT(*) FROM userentry"
    assert final_state["subtask_results"][0]["columns"] == ["count"]
    assert final_state["subtask_results"][0]["rows"] == [(42,)]
    assert final_state["final_answer"] is not None