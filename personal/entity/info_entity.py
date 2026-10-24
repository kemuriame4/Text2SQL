from dataclasses import dataclass
from personal.entity.base_entity import BaseEntity


@dataclass
class TableInfoEntity(BaseEntity):
    """
    id: 主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    """

    id: str | None = None
    name: str | None = None
    role: str | None = None
    description: str | None = None


@dataclass
class MetricInfoEntity(BaseEntity):
    """
    id: 主键id
    name: 指标名称
    description: 指标描述
    alias: 指标别名
    relevant_columns: 指标关联列
    """

    id: str | None = None
    name: str | None = None
    description: str | None = None
    alias: list[str] | None = None
    relevant_columns: list[str] | None = None
