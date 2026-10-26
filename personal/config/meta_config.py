from omegaconf import OmegaConf
from dataclasses import dataclass


@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool


@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]


@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


@dataclass
class MetaConfig:
    tables: list[TableConfig]
    metrics: list[MetricConfig]


context = OmegaConf.load("meta_config.yaml")
schema = OmegaConf.structured(MetaConfig)

meta_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
