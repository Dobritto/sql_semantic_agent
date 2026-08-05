import json
from agent.schemas import (
    RouterResult,
    SQLToolParams,
    TextAnswerToolParams,
    ClarificationToolParams,
    RejectToolParams,
)
from llm.llm_client import LLMClient
from prompts.tech_prompts import TOOLS_DESCRIPTION


class Router:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def route(self, question: str) -> RouterResult:
        prompt = f"""
        Ты — router аналитического агента для образовательной платформы Simulative.

        На платформе пользователи решают задачи по программированию и проходят тесты.
        В БД есть данные только за 2021-2022 год.

        Доступные tools:
        {TOOLS_DESCRIPTION}

        Вопрос пользователя: {question}

        Верни ТОЛЬКО валидный JSON без markdown и пояснений:
        {{
            "tool": "название tool",
            "reasoning": "почему выбрал этот tool",
            "params": {{
                // для sql_tool: {{"question": "вопрос"}}
                // для text_answer_tool: {{"answer": "готовый ответ"}}
                // для clarification_tool: {{"clarification_question": "что уточнить"}}
                // для reject_tool: {{"reason": "причина отказа"}}
            }}
        }}
        """
        raw = self.llm.ask(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)
        print(f'data: {data}')
        tool = data['tool']
        params_data = data['params']

        if tool == "sql_tool":
            params = SQLToolParams(**params_data)
        elif tool == "text_answer_tool":
            params = TextAnswerToolParams(**params_data)
        elif tool == "clarification_tool":
            params = ClarificationToolParams(**params_data)
        elif tool == "reject_tool":
            params = RejectToolParams(**params_data)
        else:
            raise ValueError(f"Неизвестный tool: {tool}")

        return RouterResult(
            tool=tool,
            params=params,
            reasoning=data['reasoning']
        )