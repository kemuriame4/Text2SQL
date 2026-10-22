from dataclasses import dataclass


@dataclass
class TableConfig :
    name:str
    role:str
    description:str
    columns :list[str]

@dataclass
class ColumnsConfig :
    name:str
    role:str
    description:str
    alias:list[str]
    sync:bool

@dataclass
class MetricConfig :
    name:str
    description:str
    alias:list[str]
    relevant_columns:list[str]
    sync:bool
@dataclass
class MetaConfig:
    tables:TableConfig
    metrics:MetricConfig

