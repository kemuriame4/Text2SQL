from sqlalchemy import String, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase


class ColumnMetricModel(CommonBase):
    __tablename__ = 't_column_metric'
    column_id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='字段id')
    metric_id:Mapped[str] = mapped_column(String(64),primary_key=True,comment='指标id')


