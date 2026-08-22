from typing import Callable

from llm.llm_client import LLMClient
from agent.graph_state import AgentState


def make_fix_sql_node(llm: LLMClient) -> Callable[[AgentState], dict]:
    def fix_sql(state: AgentState) -> dict:
        sql = llm.fix_sql(state["current_sql"], state["sql_error"], state["current_prompt"])
        fixed_sql = sql.replace("```sql", "").replace("```", "").strip()

        return {'current_sql': fixed_sql}

    return fix_sql
