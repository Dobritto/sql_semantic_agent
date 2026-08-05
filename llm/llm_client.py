import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
import time

load_dotenv()


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ['OPENROUTER_API_KEY'],
            base_url="https://openrouter.ai/api/v1",
        )
        self.models = [
            "nvidia/nemotron-3-super-120b-a12b:free",
            # 'qwen/qwen3-coder:free',
            "openai/gpt-oss-120b:free",
            "meta-llama/llama-3.3-70b-instruct:free"
        ]

    def ask(self, prompt: str, retries: int = 3) -> str:
        for model in self.models:
            for attempt in range(retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                    )
                    return response.choices[0].message.content

                # except RateLimitError:
                #     wait = 30 * (attempt + 1)
                #     print(f"Rate limit на {model}, жду {wait}с...")
                #     time.sleep(wait)

                except Exception as e:
                    print(f"Ошибка на {model}: {e}")
                    break  # переходим к следующей модели

        raise RuntimeError('Все модели недоступны')

    def fix_sql(self, sql: str, error: str, prompt: str) -> str:
        """
        Отправляет в LLM сломанный SQL + текст ошибки.
        Просит исправить и вернуть рабочий SQL
        """
        fix_prompt = f"""
        Ты аналитик данных. Ты сгенерировал SQL-запрос, но он упал с ошибкой.

        Исправь запрос и верни ТОЛЬКО исправленный SQL без пояснений и без markdown.

        ## Оригинальный контекст задачи
        {prompt}

        ## SQL который упал с ошибкой
        {sql}

        ## Текст ошибки
        {error}
        """
        return self.ask(fix_prompt)
