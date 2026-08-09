from typing import Callable

from agent.graph_state import AgentState
from agent.router import Router


def make_route_question_node(router: Router) -> Callable[[AgentState], dict]:
    def route_question(state: AgentState) -> dict:
        route = router.route(state['question'])
        return {"route": route}

    return route_question
