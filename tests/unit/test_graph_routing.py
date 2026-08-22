import pytest

from agent.graph import build_graph
from agent.schemas import (
    RouterResult,
    TextAnswerToolParams,
    ClarificationToolParams,
    RejectToolParams,
)
from tests.conftest import StubRouter


@pytest.mark.parametrize(
    "route_result, expected_answer",
    [
        (
            RouterResult(
                tool="text_answer_tool",
                params=TextAnswerToolParams(answer="MAU — это..."),
                reasoning="термин",
            ),
            "MAU — это...",
        ),
        (
            RouterResult(
                tool="clarification_tool",
                params=ClarificationToolParams(clarification_question="За какой период?"),
                reasoning="размыто",
            ),
            "За какой период?",
        ),
        (
            RouterResult(
                tool="reject_tool",
                params=RejectToolParams(reason="не по теме"),
                reasoning="оффтоп",
            ),
            "не по теме",
        ),
    ],
)
def test_graph_routes_to_correct_terminal_node(route_result, expected_answer):
    graph = build_graph(StubRouter(route_result), decomposer=None, available_metrics=[])

    final_state = graph.invoke({
        "question": "сколько активных пользователей за 2022 год",
        "route": None,
        "final_answer": None,
        "decomposition_result": None,
        "subtask_index": 0,
        "current_sql": None,
        "subtask_results": []
    })

    assert final_state["final_answer"] == expected_answer