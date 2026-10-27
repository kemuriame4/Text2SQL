# 【文件作用】
# 这个文件定义"一条字段（列）信息"在代码里长什么样（entity 盒子）。
# 它只负责装数据，不连数据库；数据库那一侧对应 app/model/column_info_model.py。
import datetime  # 导入 datetime 模块（本文件暂时没用到，保留原样）
from typing import Any  # 导入 Any（表示"任意类型"，用在 examples 列表里，元素类型不限）

from pydantic.dataclasses import dataclass  # 导入 pydantic 版的 dataclass（带类型校验的"数据盒子"写法）

from app.entity.common_entity import CommonBaseEntity  # 导入公共基础 entity，获得 del_flag/创建人/修改人等公共字段


@dataclass  # 套上 pydantic dataclass 装饰器：自动生成初始化方法，并在创建对象时校验类型
class ColumnInfoEntity(CommonBaseEntity):  # 定义"字段信息"entity 类，继承公共字段
    '''
    id  主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    '''
    id:str | None = None  # 主键 id：唯一标识一个字段，默认空
    name:str | None = None  # 字段名称：数据库里这一列叫什么，默认空
    role:str | None = None  # 字段角色：primary_key 主键 / foreign_key 外键 / measure 度量 / dimension 维度，默认空
    description:str| None = None  # 字段描述：这一列的业务含义，默认空
    type: str | None = None  # 数据类型：如 varchar/int/decimal，默认空
    alias: list[str]| None = None  # 别名列表：这一列的其他叫法（同义词），默认空
    table_id: str | None = None  # 所属表 id（外键，指向 t_table_info.id），默认空
    examples: list[Any] | None = None  # 数据示例列表：这一列真实数据长什么样，默认空
    # qdrant_id: str | None = None
