from langgraph.graph import StateGraph, END

from agent.graph_state import AgentState
from agent.decomposer import Decomposer
from agent.router import Router
from agent.nodes.router_question import make_route_question_node
from agent.nodes.decompose_question import make_decompose_question_node
from agent.nodes.terminal_answer import answer_directly, ask_clarification, reject
from agent.nodes.generate_sql import make_generate_sql_node
from agent.nodes.execute_sql import make_execute_sql_node
from agent.nodes.fix_sql import make_fix_sql_node
from agent.nodes.summarize import summarize
from agent.nodes.record_subtask_result import record_subtask_result
from rag.rag_client import SemanticIndex
from llm.llm_client import LLMClient
from db.db_client import DBClient


def route_after_routing(state: AgentState) -> str:
    return state["route"].tool


def _sql_success_placeholder(state: AgentState) -> dict:
    return {"final_answer": f"SQL выполнен успешно. Строк: {len(state['sql_rows'])}. Данные: {state['sql_rows']}"}


def _sql_give_up(state: AgentState) -> dict:
    return {
        "final_answer": f"Не удалось выполнить запрос после {MAX_ATTEMPTS} попыток. Последняя ошибка: {state['sql_error']}"}

def route_after_subtask(state: AgentState) -> str:
    if state["subtask_index"] < len(state["decomposition_result"].subtasks):
        return "next_subtask"
    return "all_done"


MAX_ATTEMPTS = 3


def route_after_execute(state: AgentState) -> str:
    if state["sql_error"] is None:
        return "success"
    if state["attempt"] >= MAX_ATTEMPTS:
        return "give_up"
    return "retry"


def build_graph(router: Router,
                decomposer: Decomposer,
                available_metrics: list[str],
                si: SemanticIndex = None,
                llm: LLMClient = None,
                db: DBClient = None):
    graph = StateGraph(AgentState)

    graph.add_node("route_question", make_route_question_node(router))
    graph.add_node("answer_directly", answer_directly)
    graph.add_node("ask_clarification", ask_clarification)
    graph.add_node("reject", reject)
    graph.add_node("decompose_question",
                   make_decompose_question_node(decomposer, available_metrics))
    graph.add_node("generate_sql", make_generate_sql_node(si, llm))
    graph.add_node("execute_sql", make_execute_sql_node(db))
    graph.add_node("fix_sql", make_fix_sql_node(llm))
    graph.add_node("sql_give_up", _sql_give_up)
    graph.add_node("record_subtask_result", record_subtask_result)
    graph.add_node("summarize", summarize)
    graph.set_entry_point("route_question")

    graph.add_conditional_edges(
        "route_question",
        route_after_routing,
        {
            "sql_tool": "decompose_question",
            "text_answer_tool": "answer_directly",
            "clarification_tool": "ask_clarification",
            "reject_tool": "reject",
        },
    )

    graph.add_edge("answer_directly", END)
    graph.add_edge("ask_clarification", END)
    graph.add_edge("reject", END)
    graph.add_edge("decompose_question", "generate_sql")
    graph.add_edge("generate_sql", "execute_sql")
    graph.add_conditional_edges(
        "execute_sql",
        route_after_execute,
        {
            "success": "record_subtask_result",
            "retry": "fix_sql",
            "give_up": "sql_give_up",
        },
    )
    graph.add_edge("fix_sql", "execute_sql")
    graph.add_conditional_edges(
        "record_subtask_result",
        route_after_subtask,
        {
            "next_subtask": "generate_sql",
            "all_done": "summarize"
        }
    )
    graph.add_edge("sql_give_up", END)
    graph.add_edge("summarize", END)
    return graph.compile()
