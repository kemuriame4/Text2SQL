# 【文件作用】
# 这个文件是数据库表 t_column_metric（字段-指标关联表）在代码里的镜像（model），是一张多对多中间表。
# repository 层通过它读写数据库；代码各层之间传数据用 app/entity/column_metric_entity.py。
from sqlalchemy import String, CHAR  # 导入列类型：String 变长字符串、CHAR 定长字符串（本文件 CHAR 没用到，保留原样）
from sqlalchemy.orm import Mapped, mapped_column  # 导入 Mapped（标注 Python 类型）和 mapped_column（定义数据库列）

from app.model.common_base import CommonBase  # 导入公共 model 基类，获得公共列


class ColumnMetricModel(CommonBase):  # 定义"字段-指标关联" model 类，对应数据库里的 t_column_metric 表
    __tablename__ = 't_column_metric'  # 指定这个类映射的真实表名
    column_id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='字段id')  # 字段 id（外键，指向 t_column_info.id）；primary_key=True 表示它是联合主键的一部分
    metric_id:Mapped[str] = mapped_column(String(64),primary_key=True,comment='指标id')  # 指标 id（外键，指向 t_metric_info.id）；primary_key=True 表示它是联合主键的另一部分


