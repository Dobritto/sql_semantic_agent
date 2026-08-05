from datetime import date
import re
from dataclasses import dataclass

from src.semantic_layer import SemanticLayer

MONTHS_RU = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
}

@dataclass
class ParsedIntent:
    question: str
    metric_id: str | None
    dimensions: list[str]
    date_from: str | None
    date_to: str | None
    needs_clarification: bool
    clarification_reason: str | None

class IntentParser:
    def __init__(self, semantic_layer: SemanticLayer):
        self.semantic_layer = semantic_layer

    def parse(self, question: str) -> ParsedIntent:
        metric_result = self.semantic_layer.find_metric(question)
        dimensions_result = self.semantic_layer.find_dimensions(question)
        period = self._parse_month_period(question)

        metric_id = metric_result[0] if metric_result else None
        dimensions = [dim_id for dim_id, _ in dimensions_result]

        needs_clarification = False  # Разъяснение
        clarification_reason = None

        if metric_id is None:
            needs_clarification = True
            clarification_reason = "Не удалось определить метрику."

        if period is None:
            needs_clarification = True
            clarification_reason = "Не указан период расчёта."

        date_from = period[0] if period else None
        date_to = period[1] if period else None

        return ParsedIntent(
            question=question,
            metric_id=metric_id,
            dimensions=dimensions,
            date_from=date_from,
            date_to=date_to,
            needs_clarification=needs_clarification,
            clarification_reason=clarification_reason,
        )

    def _parse_month_period(self, question: str) -> tuple[str, str] | None:
        question_lower = question.lower()

        year_match = re.search(r"\b(20\d{2})\b", question_lower)
        if not year_match:
            return None
        year = int(year_match.group(1))

        for month_name, month_number in MONTHS_RU.items():
            if month_name in question_lower:
                date_from = date(year, month_number, 1)

                if month_number == 12:
                    date_to = date(year + 1, 1, 1)
                else:
                    date_to = date(year, month_number + 1, 1)

                return date_from.isoformat(), date_to.isoformat()

        return None