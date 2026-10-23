from pydantic.dataclasses import dataclass

@dataclass
class ColumnConfig():
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool

@dataclass
class TableConfig():
    name: str
    role: str
    description: str
    column:list[ColumnConfig]

@dataclass
class MetricConfig():
    name: str
    description: str
    relevent_columns:list[str]
    alias: list[str]

@dataclass
class MetaConfig:
    tables: list[TableConfig]
    metrics:list[MetricConfig]