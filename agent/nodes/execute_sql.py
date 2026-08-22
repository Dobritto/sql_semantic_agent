from typing import Callable
from db.db_client import DBClient
from agent.graph_state import AgentState


def make_execute_sql_node(db: DBClient) -> Callable[[AgentState], dict]:
    def execute_sql(state: AgentState) -> dict:

        if not state["current_sql"].lstrip().upper().startswith("SELECT"):
            return {"sql_error": "разрешены только SELECT-запросы",
                    "attempt": state["attempt"] + 1}

        else:

            success, columns_or_error, rows = db.run(state["current_sql"])

            if success:
                return {"sql_columns": columns_or_error, "sql_rows": rows, "sql_error": None}
            else:
                return {"sql_error": columns_or_error, "attempt": state["attempt"] + 1}

    return execute_sql
