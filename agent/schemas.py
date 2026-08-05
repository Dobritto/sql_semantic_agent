from pydantic import BaseModel
from typing import List, Literal, Union


class SubTask(BaseModel):
    question: str
    metric_id: str
    date_from: str
    date_to: str


class DecompositionResult(BaseModel):
    is_complex: bool
    subtasks: List[SubTask]
    reasoning: str


class SQLToolParams(BaseModel):
    question: str


class TextAnswerToolParams(BaseModel):
    answer: str


class ClarificationToolParams(BaseModel):
    clarification_question: str  # Уточнение


class RejectToolParams(BaseModel):
    reason: str


class RouterResult(BaseModel):
    """
    Результат работы Router.
    tool — какой инструмент вызвать.
    params — параметры инструмента, зависят от tool.
    reasoning — почему выбрал этот tool.
    """
    tool: Literal['sql_tool', 'text_answer_tool', 'clarification_tool', 'reject_tool']
    params: Union[SQLToolParams, TextAnswerToolParams, ClarificationToolParams, RejectToolParams]
    reasoning: str
