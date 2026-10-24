from sqlalchemy import Text, String, JSON
from sqlalchemy.orm import mapped_column, Mapped
from personal.model.base_model import BaseModel


class TableInfoModel(BaseModel):
    __tablename__ = "t_table_info"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, comment="主键id")
    name: Mapped[str] = mapped_column(String(64), comment="名称")
    role: Mapped[str] = mapped_column(String(64), comment="角色 0:维度表 1:事实表 ")
    description: Mapped[str] = mapped_column(String(255), comment="描述")


class MetricInfoModel(BaseModel):
    __tablename__ = "t_metric_info"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, comment="主键id")
    name: Mapped[str] = mapped_column(String(64), comment="名称")
    description: Mapped[str] = mapped_column(Text, comment="描述")
    alias: Mapped[str] = mapped_column(JSON, comment="别名")
    relevant_columns: Mapped[str] = mapped_column(JSON, comment="关联关系")
