from agent.graph_state import AgentState


def summarize(state: AgentState) -> dict:
    if not state["subtask_results"]:
        return {"final_answer": "Не удалось получить данные по запросу"}

    blocks = []
    for sub_res in state["subtask_results"]:
        blocks.append(_format_subtask_result(sub_res))

    final_answer = "\n\n".join(blocks)
    return {"final_answer": final_answer}


def _format_subtask_result(sub_res: dict) -> str:
    if not sub_res["rows"]:
        return f"{sub_res['question']}: Данных не найдено"

    elif len(sub_res["rows"]) == 1 and len(sub_res["columns"]) == 1:
        return f"{sub_res['question']}: {sub_res['rows'][0][0]}"

    elif len(sub_res["rows"]) > 1:

        header = " | ".join(sub_res["columns"])

        lines = []

        for row in sub_res["rows"]:
            lines.append(" | ".join(str(value) for value in row))

        return f"{sub_res['question']}:\n{header}\n" + "\n".join(lines)
