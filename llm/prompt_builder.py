# Для каждой таблицы, которая может быть базовой (requires_tables[0] метрики) —
# алиас и колонка с датой события. Соответствует алиасам, которые уже используются
# в JOIN-ах измерений (config/simulative_semantic_layer.yaml -> dimensions).
BASE_TABLE_META = {
    "userentry": {"alias": "ue", "date_column": "entry_at"},
    "users": {"alias": "u", "date_column": "date_joined"},
    "codesubmit": {"alias": "cs", "date_column": "created_at"},
    "coderun": {"alias": "cr", "date_column": "created_at"},
    "transaction": {"alias": "t", "date_column": "created_at"},
    "teststart": {"alias": "ts", "date_column": "created_at"},
}


def build_prompt(
        question: str,
        date_from: str,
        date_to: str,
        metric_id: str,
        dimension_ids: list[str],
        config: dict,
) -> str:
    """
    Собирает промпт для LLM из трёх частей:
    1. Схема БД
    2. Контекст метрики и измерений из yaml
    3. Задача — вопрос + период
    """

    schema = config['db_schema']

    metric = config['metrics'][metric_id]

    base_table = metric['requires_tables'][0]
    if base_table not in BASE_TABLE_META:
        raise ValueError(
            f"Для таблицы '{base_table}' (метрика '{metric_id}') не задан алиас "
            f"в BASE_TABLE_META — добавьте её в llm/prompt_builder.py"
        )
    base_alias = BASE_TABLE_META[base_table]["alias"]
    base_date_column = BASE_TABLE_META[base_table]["date_column"]

    metric_block = f"""
    Метрика: {metric['label']}
    Описание: {metric['description']}
    SQL-выражение: {metric['sql']}
    Обязательный фильтр: {metric.get('filter') or 'нет'}
    """

    examples_block = ""
    if metric.get("examples"):
        examples_block = "## Примеры готовых запросов для этой метрики\n"
        for ex in metric["examples"][:2]:  # не больше 2, чтобы не раздувать промпт
            examples_block += f"\nВопрос: {ex['question']}\nSQL:\n{ex['sql']}\n"

    dims_block = ""
    if dimension_ids:
        dims_block = "Измерение для GROUP BY:\n"
        for dim_id in dimension_ids:
            dim = config['dimensions'][dim_id]
            dims_block += f"""
            - {dim['label']}:
                SELECT: {dim['column']}
                JOIN: {dim.get('join') or 'не нужен'}
                GROUP BY: {dim['group_by']}
            """

    prompt = f"""
    Ты аналитик данных. Напиши SQL-запрос для PostgreSQL (НЕ SQLite — не используй strftime()).

    Верни ТОЛЬКО SQL без пояснений и без markdown.

    ## Схема БД
    {schema}

    ## Метрика
    {metric_block}

    ## Измерения
    {dims_block}
    {examples_block}
    ## Задача
    Вопрос пользователя: {question}
    Период: с {date_from} по {date_to} (не включительно)

    Правила:
    - Используй синтаксис PostgreSQL
    - Базовая таблица: FROM {base_table} {base_alias}
    - Подключай только те JOIN-ы которые нужны
    - Фильтр по дате: {base_alias}.{base_date_column} >= '{date_from}' AND {base_alias}.{base_date_column} < '{date_to}'
    - Применяй обязательный фильтр метрики в WHERE
    - Если есть GROUP BY — добавь ORDER BY метрике DESC
    """

    return prompt
