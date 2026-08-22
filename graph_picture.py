"""
Скрипт для визуализации структуры графа. Не выполняет граф (.invoke не
вызывается) — только собирает его через build_graph() и рисует структуру.
Поэтому реальные Router/Decomposer/LLM/DB не нужны, реальные креды и
интернет (для .env) тоже — используем те же тестовые заглушки, что и в
tests/conftest.py, просто с "пустым" содержимым, раз оно не используется.

Запуск из корня проекта:
    python render_graph.py
"""

from agent.graph import build_graph
from agent.schemas import RouterResult, SQLToolParams
from tests.conftest import StubRouter, StubDecomposer, StubSemanticIndex, StubLLMClient, StubDBClient


def main():

    dummy_route = RouterResult(
        tool="sql_tool",
        params=SQLToolParams(question="заглушка"),
        reasoning="заглушка",
    )

    graph = build_graph(
        StubRouter(dummy_route),
        StubDecomposer(None),
        available_metrics=[],
        si=StubSemanticIndex(dimensions=[], config={}),
        llm=StubLLMClient(response=""),
        db=StubDBClient([(True, [], [])]),
    )

    print("=== ASCII-схема графа ===\n")
    print(graph.get_graph().draw_ascii())

    print("\n=== Пробую сохранить PNG (нужен интернет — рендерится через mermaid.ink) ===")
    try:
        graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        print("Сохранено: graph.png")
    except Exception as e:
        print(f"Не получилось сохранить PNG: {e}")
        print("ASCII-схема выше всё равно доступна для просмотра.")


if __name__ == "__main__":
    main()