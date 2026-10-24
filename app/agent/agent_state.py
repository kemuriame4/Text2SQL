from typing import TypedDict


class AgentState(TypedDict):
    question: str
    keywords: list[str]
    is_end: bool