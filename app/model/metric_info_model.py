from sqlalchemy import String, CHAR, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase

class MetricInfoModel(CommonBase):
    __tablename__ = 't_metric_info'
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(64),comment='名称')
    description:Mapped[str] = mapped_column(Text,comment='描述')
    alias:Mapped[str] = mapped_column(JSON,comment='别名')
    relevant_columns:Mapped[str] = mapped_column(JSON,comment='关联关系')



