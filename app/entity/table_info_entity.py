from dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class TableInfoEntity(CommonBaseEntity):
    '''
    id 主键id
    name 表名称
    role 表角色 事实表 维度表
    description 描述
    '''
    id: int
    name: str
    role: str
    description: str
