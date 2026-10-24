from typing import Any
from dataclasses import dataclass
from personal.entity.base_entity import BaseEntity


@dataclass
class ColumnMetricEntity(BaseEntity):
    column_id: str | None = None
    metric_id: str | None = None


@dataclass
class ColumnInfoEntity(BaseEntity):
    """
    id: 主键id
    name: 列名
    role : 列角色   事实列、维度列
    description 列描述
    type: 列类型
    alias: 列别名
    table_id: 表id
    examples: 示例
    """

    id: str | None = None
    name: str | None = None
    role: str | None = None
    description: str | None = None
    type: str | None = None
    alias: list[str] | None = None
    table_id: str | None = None
    examples: list[Any] | None = None
