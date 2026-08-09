from typing import Callable

from agent.graph_state import AgentState
from agent.decomposer import Decomposer


def make_decompose_question_node(decomposer: Decomposer,
                                 available_metrics: list[str]) -> Callable[[AgentState], dict]:
    def decompose_question(state: AgentState) -> dict:
        decompose = decomposer.decompose(state['question'])
        return {"decompose": decompose}

    return decompose_question
