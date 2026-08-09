from agent.graph_state import AgentState


def answer_directly(state: AgentState) -> dict:
    return {"final_answer": state["route"].params.answer}


def ask_clarification(state: AgentState) -> dict:
    return {"final_answer": state["route"].params.clarification_question}


def reject(state: AgentState) -> dict:
    return {"final_answer": state["route"].params.reason}
