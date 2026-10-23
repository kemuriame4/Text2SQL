import datetime
from typing import Any

from pydantic.dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class ColumnInfoEntity(CommonBaseEntity):
    '''
    id  主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    '''
    id:str | None = None
    name:str | None = None
    role:str | None = None
    description:str| None = None
    type: str| None = None
    alias: list[str]| None = None
    table_id: str| None = None
    examples: list[Any] | None = None
