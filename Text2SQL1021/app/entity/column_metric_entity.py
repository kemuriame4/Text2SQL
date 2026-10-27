# 【文件作用】
# 这个文件定义"字段和指标的关联关系"在代码里长什么样（entity 盒子），对应多对多中间表 t_column_metric。
# 它只负责装数据，不连数据库；数据库那一侧对应 app/model/column_metric_model.py。
from pydantic.dataclasses import dataclass  # 导入 pydantic 版的 dataclass（带类型校验的"数据盒子"写法）

from app.entity.common_entity import CommonBaseEntity  # 导入公共基础 entity，获得公共字段


@dataclass  # 套上 pydantic dataclass 装饰器：自动生成初始化方法，并在创建对象时校验类型
class ColumnMetricEntity(CommonBaseEntity):  # 定义"字段-指标关联"entity 类，继承公共字段

    column_id:str | None = None  # 字段 id（外键，指向 t_column_info.id），表示关联到哪个字段，默认空
    metric_id:str | None = None  # 指标 id（外键，指向 t_metric_info.id），表示关联到哪个指标，默认空
