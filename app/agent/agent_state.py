from typing import TypedDict

from app.entity.column_info_entity import ColumnInfoEntity


class AgentState(TypedDict):
    question: str
    keywords: list[str]
    is_end: bool
    retrieval_columns: list[ColumnInfoEntity]