# 【文件作用】
# 这个文件是数据库表 t_metric_info（指标信息表）在代码里的镜像（model）。
# repository 层通过它读写数据库；代码各层之间传数据用 app/entity/metric_info_entity.py。
from sqlalchemy import String, CHAR, Text, JSON  # 导入列类型：String 变长字符串、CHAR 定长字符串（未用到）、Text 长文本、JSON 结构化数据
from sqlalchemy.orm import Mapped, mapped_column  # 导入 Mapped（标注 Python 类型）和 mapped_column（定义数据库列）

from app.model.common_base import CommonBase  # 导入公共 model 基类，获得公共列

class MetricInfoModel(CommonBase):  # 定义指标信息 model 类，对应数据库里的 t_metric_info 表
    __tablename__ = 't_metric_info'  # 指定这个类映射的真实表名
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')  # 主键 id：唯一标识一个指标；primary_key=True 表示主键
    name:Mapped[str] = mapped_column(String(64),comment='名称')  # 指标名称：如 GMV、订单量，最长 64 字符
    description:Mapped[str] = mapped_column(Text,comment='描述')  # 指标描述：这个指标怎么算、代表什么，用 Text 存长文本
    alias:Mapped[str] = mapped_column(JSON,comment='别名')  # 别名：这个指标的其他叫法，JSON 类型（存数组）
    relevant_columns:Mapped[str] = mapped_column(JSON,comment='关联关系')  # 关联字段：算这个指标要用到哪些字段，JSON 类型（存数组）



