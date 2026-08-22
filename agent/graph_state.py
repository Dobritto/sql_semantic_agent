from typing import TypedDict

from agent.schemas import RouterResult, DecompositionResult

class AgentState(TypedDict):
    question: str
    route: RouterResult | None
    final_answer: str | None
    decomposition_result: DecompositionResult | None
    subtask_index: int
    current_sql: str | None
    current_prompt: str | None
    sql_error: str | None
    attempt: int
    sql_columns: list[str] | None
    sql_rows: list[tuple] | None
    subtask_results: list[dict]