from typing import TypedDict

from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.metric_info_entity import MetricInfoEntity
from app.entity.value_info import ValueInfo


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]

class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]

class MetricInfoState(TypedDict):
    name: str
    description: str
    retrieval_columns: list[str]
    alias: list[str]



class AgentState(TypedDict):
    question: str
    keywords: list[str]
    is_end: bool
    retrieval_columns: list[ColumnInfoEntity]
    retrieval_metrics: list[MetricInfoEntity]
    retrieval_values: list[ValueInfo]

    table_infos: list[TableInfoState]
    metric_infos: list[MetricInfoState]