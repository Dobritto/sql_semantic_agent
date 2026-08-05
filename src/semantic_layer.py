from pathlib import Path
from typing import Any
import pymorphy3
import yaml


class SemanticLayer:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.config = self._load()
        self.morph = pymorphy3.MorphAnalyzer()

    def _load(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    @property
    def metrics(self) -> dict[str, Any]:
        return self.config["metrics"]

    @property
    def dimensions(self) -> dict[str, Any]:
        return self.config["dimensions"]

    def _lemmatize_text(self, text: str) -> set[str]:
        words = text.lower().replace(",", " ").replace("?", " ").replace(".", " ").split()

        lemmas = set()
        for word in words:
            parsed = self.morph.parse(word)[0]
            lemmas.add(parsed.normal_form)

        return lemmas

    def _is_alias_matched(self, alias: str, question: str) -> bool:
        alias_lemmas = self._lemmatize_text(alias)
        question_lemmas = self._lemmatize_text(question)

        return alias_lemmas.issubset(question_lemmas)

    def find_metric(self, question: str) -> tuple[str, dict[str, Any]] | None:
        for metric_id, metric in self.metrics.items():
            aliases = metric.get("aliases", [])

            for alias in aliases:
                if self._is_alias_matched(alias, question):
                    return metric_id, metric

        return None

    def find_dimensions(self, question: str) -> list[tuple[str, dict[str, Any]]]:
        found = []

        for dimension_id, dimension in self.dimensions.items():
            aliases = dimension.get("aliases", [])

            for alias in aliases:
                if self._is_alias_matched(alias, question):
                    found.append((dimension_id, dimension))
                    break

        return found
