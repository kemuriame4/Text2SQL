from dataclasses import dataclass

from typing import Any

from app.entity.common_entity  import CommonBaseEntity

@dataclass
class ColumnInfoEntity(CommonBaseEntity):
    '''
        id  主键id，格式为 表名.字段名，例如 fact_order.order_amount
        name: 字段名称
        role : 字段角色  primary_key / foreign_key / measure / dimension
        description 字段描述
        type 字段在数仓里的真实数据类型
        alias 字段别名（用于向量检索召回）
        examples 字段的真实取值样例（让大模型知道该字段长什么样）
        table_id 所属表 id，外键指向 t_table_info.id
        '''

    id:str | None = None
    name:str | None = None
    role:str | None = None
    description: str | None = None
    type: str | None = None
    alias: list[str] | None = None
    table_id: str | None = None
    examples: list[Any] | None = None