"""表信息的业务实体：在 service / mapper 之间传递的"表"对象。"""
from pydantic.dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class TableInfoEntity(CommonBaseEntity):
    '''
    id  主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    '''
    # 字段（下面 4 个是本类新增，其余继承自 CommonBaseEntity）：
    # id (str | None)：主键，实际存表名，如 dim_region。
    # name (str | None)：表名称。
    # role (str | None)：表角色，取值 dim / fact（由 meta_config.yaml 决定）。
    # description (str | None)：表的中文说明。
    id:str | None = None
    name:str | None = None
    role:str | None = None
    description:str | None = None
