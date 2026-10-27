# 【文件作用】
# 这个文件定义"一条指标信息"（如 GMV、订单量）在代码里长什么样（entity 盒子）。
# 它只负责装数据，不连数据库；数据库那一侧对应 app/model/metric_info_model.py。
from pydantic.dataclasses import dataclass  # 导入 pydantic 版的 dataclass（带类型校验的"数据盒子"写法）

from app.entity.common_entity import CommonBaseEntity  # 导入公共基础 entity，获得公共字段


@dataclass  # 套上 pydantic dataclass 装饰器：自动生成初始化方法，并在创建对象时校验类型
class MetricInfoEntity(CommonBaseEntity):  # 定义"指标信息"entity 类，继承公共字段

    id:str | None = None  # 主键 id：唯一标识一个指标，默认空
    name:str | None = None  # 指标名称：如 GMV、订单量，默认空
    description:str | None = None  # 指标描述：这个指标怎么算、代表什么，默认空
    alias: list[str] | None = None  # 别名列表：这个指标的其他叫法（同义词），默认空
    relevant_columns: list[str] | None = None  # 关联字段 id 列表：算这个指标要用到哪些字段，默认空
