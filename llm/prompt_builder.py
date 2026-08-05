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
    metric_block = f"""
    Метрика: {metric['label']}
    Описание: {metric['description']}
    SQL-выражение: {metric['sql']}
    Обязательный фильтр: {metric.get('filter') or 'нет'}
    """

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
        # --- Собираем всё вместе ---
    prompt = f"""
    Ты аналитик данных. Напиши SQL-запрос для SQLite.

    Верни ТОЛЬКО SQL без пояснений и без markdown.

    ## Схема БД
    {schema}

    ## Метрика
    {metric_block}

    ## Измерения
    {dims_block}

    ## Задача
    Вопрос пользователя: {question}
    Период: с {date_from} по {date_to} (не включительно)

    Правила:
    - Используй синтаксис Postgres SQL
    - Базовая таблица: FROM orders o
    - Подключай только те JOIN-ы которые нужны
    - Фильтр по дате: o.order_date >= '{date_from}' AND o.order_date < '{date_to}'
    - Применяй обязательный фильтр метрики в WHERE
    - Если есть GROUP BY — добавь ORDER BY метрике DESC
    """

    return prompt
