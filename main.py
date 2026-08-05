from llm.prompt_builder import build_prompt
from rag.rag_client import SemanticIndex
from llm.llm_client import LLMClient
from db.db_client import DBClient
from agent.decomposer import Decomposer
from agent.router import Router

si = SemanticIndex("config/simulative_semantic_layer.yaml")
llm = LLMClient()
db = DBClient(
    db_type="postgres",
    host="95.163.241.236",
    port=5432,
    dbname="simulative",
    user="student",
    password="qweasd963",
)
decomposer = Decomposer(llm)
MAX_ATTEMPTS = 3

router = Router(llm)
# question = "Какой месяц был лучшим по регистрациям и по активности за 2022 год?"
question = 'Рассчитай 30-day retention для клиентов, которые зарегистрировались в мае 2022 года'

route_result = router.route(question)
print(f"\nRouter выбрал: {route_result.tool}")
print(f"Reasoning: {route_result.reasoning}")

if route_result.tool == 'sql_tool':

    available_metrics = list(si.config['metrics'].keys())

    print(f'Вопрос: {question}')
    decomposition = decomposer.decompose(question, available_metrics)

    print('Декомпозиция:')
    print(f'difficult question: {decomposition.is_complex}')
    print(f'Reasoning: {decomposition.reasoning}')
    print(f'Number of subtasks: {len(decomposition.subtasks)}')

    all_results = []

    for i, subtask in enumerate(decomposition.subtasks, 1):
        print(f'Подзадача {i}: {subtask.question}')
        dimensions = si.find_dimensions(question, threshold=0.45)
        dim_ids = [d[0] for d in dimensions]

        prompt = build_prompt(
            question=subtask.question,
            date_from=subtask.date_from,
            date_to=subtask.date_to,
            metric_id=subtask.metric_id,
            dimension_ids=dim_ids,
            config=si.config,
        )

        sql = llm.ask(prompt)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f'Попытка {attempt}')
            print(sql)

            success, result, rows = db.run(sql)

            if success:
                columns = result
                print('Результат:')
                print(" | ".join(columns))
                print('-' * 40)

                for row in rows:
                    print(" | ".join(str(v) for v in row))

                all_results.append({
                    "question": subtask.question,
                    "columns": columns,
                    "rows": rows
                })
                break

            else:
                error = result
                print(f'Ошибка: {error}')

                if attempt == MAX_ATTEMPTS:
                    print('Failed to fix SQL')
                    break

                print('I ask LLM to fix this SQL')
                sql = llm.fix_sql(sql=sql, error=error, prompt=prompt)


    print("----Итоговый ответ------")
    summary_prompt = f"""
    Пользователь спросил: {question}
    
    Вот результаты по каждой задаче:
    """
    for r in all_results:
        summary_prompt += f"Вопрос: {r['question']}\n"
        summary_prompt += " | ".join(r["columns"]) + "\n"
        for row in r["rows"][:10]:  # передаём не более 10 строк
            summary_prompt += " | ".join(str(v) for v in row) + "\n"
        summary_prompt += "\n"

    summary_prompt += "Дай краткий аналитический ответ на исходный вопрос"

    answer = llm.ask(summary_prompt)
    print(answer)

elif route_result.tool == "text_answer_tool":
    print(f"\nОтвет: {route_result.params.answer}")

elif route_result.tool == "clarification_tool":
    print(f"\nУточните: {route_result.params.clarification_question}")

elif route_result.tool == "reject_tool":
    print(f"\nНе могу помочь: {route_result.params.reason}")