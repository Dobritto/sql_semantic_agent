from typing import Callable
from llm.llm_client import LLMClient
from llm.prompt_builder import build_prompt
from rag.rag_client import SemanticIndex
from agent.graph_state import AgentState
from agent.schemas import SubTask

def make_generate_sql_node(si: SemanticIndex, llm: LLMClient) -> Callable[[AgentState], dict]:
    def generate_sql(state: AgentState) -> dict:
        subtask = state["decomposition_result"].subtasks[state["subtask_index"]]
        dimensions = si.find_dimensions(subtask.question, threshold=0.45)
        dim_ids = [x[0] for x in dimensions]
        prompt = build_prompt(
            question=subtask.question,
            date_from=subtask.date_from,
            date_to=subtask.date_to,
            metric_id=subtask.metric_id,
            dimension_ids=dim_ids,
            config=si.config,
        )
        sql = llm.ask(prompt)
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return {"current_sql": sql, "current_prompt": prompt}

    return generate_sql
