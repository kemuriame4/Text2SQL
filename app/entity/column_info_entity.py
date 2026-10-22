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
    id:str
    name:str
    role:str
    description:str
    type: str
    alias: list[str]
    table_id: str
    examples: list[Any]
