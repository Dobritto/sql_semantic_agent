from agent.nodes.summarize import summarize, _format_subtask_result


def test_format_single_row_single_column():
    sub_res = {
        "question": "сколько активных пользователей за 2022 год",
        "sql": "...",
        "columns": ["count"],
        "rows": [(1284,)],
    }
    result = _format_subtask_result(sub_res)
    assert result == "сколько активных пользователей за 2022 год: 1284"


def test_format_multiple_rows_grouped():
    sub_res = {
        "question": "сколько активных пользователей по компаниям за 2022 год",
        "sql": "...",
        "columns": ["name", "count"],
        "rows": [
            ("Яндекс.Практикум", 412),
            ("Skillbox", 350),
            ("Нетология", 522),
        ],
    }
    result = _format_subtask_result(sub_res)
    expected = (
        "сколько активных пользователей по компаниям за 2022 год:\n"
        "name | count\n"
        "Яндекс.Практикум | 412\n"
        "Skillbox | 350\n"
        "Нетология | 522"
    )
    assert result == expected


def test_format_empty_rows():
    sub_res = {
        "question": "сколько активных пользователей за 2019 год",
        "sql": "...",
        "columns": ["count"],
        "rows": [],
    }
    result = _format_subtask_result(sub_res)
    assert result == "сколько активных пользователей за 2019 год: Данных не найдено"


def test_summarize_multiple_subtasks():
    state = {
        "subtask_results": [
            {
                "question": "сколько активных пользователей за 2022 год",
                "sql": "...",
                "columns": ["count"],
                "rows": [(1284,)],
            },
            {
                "question": "сколько успешных решений задач за 2022 год",
                "sql": "...",
                "columns": ["count"],
                "rows": [(3560,)],
            },
        ]
    }
    result = summarize(state)
    expected = (
        "сколько активных пользователей за 2022 год: 1284\n\n"
        "сколько успешных решений задач за 2022 год: 3560"
    )
    assert result == {"final_answer": expected}


def test_summarize_empty_subtask_results():
    state = {"subtask_results": []}
    result = summarize(state)
    assert result == {"final_answer": "Не удалось получить данные по запросу"}