from pydantic.dataclasses import dataclasses
from app.entity.common_entity import CommonBaseEntity

@dataclasses
class TableInfoEntity(CommonBaseEntity):
    '''
    id  :主键id
    name  :表名称
    role  :表角色   事实表、维度表
    description  :表描述
    '''
    id:str | None = None
    name:str | None = None
    role:str | None = None
    description:str | None = None