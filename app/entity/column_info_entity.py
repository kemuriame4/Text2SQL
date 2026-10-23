"""字段信息的业务实体：在 service / mapper 之间传递的"字段"对象。"""
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
    # 字段（本类的，其余继承自 CommonBaseEntity）：
    # id (str | None)：主键，格式"表名.字段名"，如 dim_region.region_name。
    # name (str | None)：字段名。
    # role (str | None)：字段角色，primary_key / foreign_key / measure / dimension。
    # description (str | None)：字段中文说明。
    # type (str | None)：数据库里的真实类型，如 varchar(64)。
    # alias (list[str] | None)：字段别名列表。
    # table_id (str | None)：所属表的 id。
    # examples (list[Any] | None)：示例取值列表，如 ['华东', '华南']。
    id:str | None = None
    name:str | None = None
    role:str | None = None
    description:str| None = None
    type: str| None = None
    alias: list[str]| None = None
    table_id: str| None = None
    examples: list[Any] | None = None
    # qdrant_id: str | None = None

