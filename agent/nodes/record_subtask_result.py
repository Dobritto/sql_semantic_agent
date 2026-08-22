from agent.graph_state import AgentState


def record_subtask_result(state: AgentState) -> dict:
    subtask = state["decomposition_result"].subtasks[state["subtask_index"]]

    new_record = {"question": subtask.question,
                  "sql": state["current_sql"],
                  "columns": state["sql_columns"],
                  "rows": state["sql_rows"]}

    return {"subtask_results": state["subtask_results"] + [new_record],
            "current_sql": None,
            "current_prompt": None,
            "sql_error": None,
            "sql_columns": None,
            "sql_rows": None,
            "attempt": 0,
            "subtask_index": state["subtask_index"] + 1}