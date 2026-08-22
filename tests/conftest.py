from agent.schemas import RouterResult, DecompositionResult

class StubRouter:
    """Тестовый двойник Router — возвращает заранее заданный результат
    вместо реального похода в LLM."""

    def __init__(self, result: RouterResult):
        self._result = result

    def route(self, question: str) -> RouterResult:
        return self._result


class StubDecomposer:
    """Тестовый двойник Decomposer — возвращает заранее заданный результат
    вместо реального похода в LLM."""

    def __init__(self, result: DecompositionResult):
        self._result = result

    def decompose(self, question: str, available_metrics: list[str]) -> DecompositionResult:
        return self._result

class StubSemanticIndex:
    """Тестовый двойник SemanticIndex — не грузит модель эмбеддингов,
    возвращает заранее заданные dimensions и хранит мини-конфиг метрик."""

    def __init__(self, dimensions: list[tuple[str, float]], config: dict):
        self._dimensions = dimensions
        self.config = config

    def find_dimensions(self, question: str, threshold: float = 0.45) -> list[tuple[str, float]]:
        return self._dimensions


class StubLLMClient:
    """Тестовый двойник LLMClient — возвращает заранее заданный текст
    вместо реального похода в OpenRouter. Один и тот же ответ отдаётся
    и на ask(), и на fix_sql() — для структурных тестов графа содержимое
    не важно, важно только что метод есть и что-то возвращает."""

    def __init__(self, response: str):
        self._response = response

    def ask(self, prompt: str) -> str:
        return self._response

    def fix_sql(self, sql: str, error: str, prompt: str) -> str:
        return self._response

class StubDBClient:
    """Тестовый двойник DBClient — не подключается к реальной БД.
    Принимает список результатов и отдаёт их по очереди при каждом
    вызове run(): первый вызов — первый элемент, второй вызов — второй,
    и так далее. Когда список кончается, повторяет последний элемент —
    удобно и для сценария "один раз упал, потом починилось" (список из
    двух элементов), и для "всегда падает" (список из одного элемента)."""

    def __init__(self, results: list[tuple[bool, list[str] | str, list[tuple] | None]]):
        self._results = results
        self._call_count = 0

    def run(self, sql: str) -> tuple[bool, list[str] | str, list[tuple] | None]:
        index = min(self._call_count, len(self._results) - 1)
        result = self._results[index]
        self._call_count += 1
        return result