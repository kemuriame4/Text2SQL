# 【文件作用】
# 这个文件定义"一条表信息"在代码里长什么样（entity 盒子）。
# 它只负责装数据，不连数据库；数据库那一侧对应 app/model/table_info_model.py。
from pydantic.dataclasses import dataclass  # 导入 pydantic 版的 dataclass（带数据类型校验的"数据盒子"写法）

from app.entity.common_entity import CommonBaseEntity  # 导入公共基础 entity，里面有 del_flag/创建人/修改人等公共字段


@dataclass  # 套上 pydantic dataclass 装饰器：自动生成初始化方法，并在创建对象时校验类型
class TableInfoEntity(CommonBaseEntity):  # 定义"表信息"entity 类，继承 CommonBaseEntity 以获得公共字段
    '''
    id  主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    '''
    id:str | None = None  # 主键 id：唯一标识一张表，默认空
    name:str | None = None  # 表名称：这张表叫什么，默认空
    role:str | None = None  # 表角色：事实表（存业务事件）或维度表（存描述信息），默认空
    description:str | None = None  # 表描述：这张表是干什么的，默认空
