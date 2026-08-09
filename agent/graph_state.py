from typing import TypedDict

from agent.schemas import RouterResult, DecompositionResult

class AgentState(TypedDict):
    question: str
    route: RouterResult | None
    final_answer: str | None
    decomposition_result: DecompositionResult | None