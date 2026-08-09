from langgraph.graph import StateGraph, END

from agent.graph_state import AgentState
from agent.router import Router
from agent.nodes.route_question import make_route_question_node
from agent.nodes.terminal_answers import answer_directly, ask_clarification, reject


def _sql_placeholder(state: AgentState) -> dict:
    return {"final_answer": "SQL-ветка ещё не реализована — следующий шаг разработки"}


def route_after_routing(state: AgentState) -> str:
    return state["route"].tool


def build_graph(router: Router):
    graph = StateGraph(AgentState)

    graph.add_node("route_question", make_route_question_node(router))
    graph.add_node("answer_directly", answer_directly)
    graph.add_node("ask_clarification", ask_clarification)
    graph.add_node("reject", reject)
    graph.add_node("sql_placeholder", _sql_placeholder)

    graph.set_entry_point("route_question")

    graph.add_conditional_edges(
        "route_question",
        route_after_routing,
        {
            "sql_tool": "sql_placeholder",
            "text_answer_tool": "answer_directly",
            "clarification_tool": "ask_clarification",
            "reject_tool": "reject",
        },
    )

    graph.add_edge("answer_directly", END)
    graph.add_edge("ask_clarification", END)
    graph.add_edge("reject", END)
    graph.add_edge("sql_placeholder", END)

    return graph.compile()