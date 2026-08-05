import json
from agent.schemas import DecompositionResult, SubTask
from llm.llm_client import LLMClient


class Decomposer:
    """
    Takes a complex questions and breaks
    it down into subtask
    """

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def decompose(self, question: str, available_metrics: list[str]) -> DecompositionResult:
        prompt = f"""
Ты аналитический агент. Твоя задача — разобрать вопрос пользователя 
и определить нужна ли декомпозиция на подзадачи.

Доступные метрики: {', '.join(available_metrics)}

Вопрос: {question}

Верни ТОЛЬКО валидный JSON строго по этой схеме, без пояснений и markdown:
{{
    "is_complex": true или false,
    "reasoning": "почему так разбил",
    "subtasks": [
        {{
            "question": "подвопрос",
            "metric_id": "одна из доступных метрик",
            "date_from": "YYYY-MM-DD",
            "date_to": "YYYY-MM-DD"
        }}
    ]
}}

Правила:
- Если вопрос простой — is_complex: false, subtasks содержит одну задачу
- Если сложный — разбей на минимальное число подзадач
- metric_id выбирай ТОЛЬКО из списка доступных метрик
- Даты извлекай из вопроса, если не указаны — используй 2022 год (данные только за 2021-2022)

"""

        raw = self.llm.ask(prompt)

        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)
        return DecompositionResult(**data)
