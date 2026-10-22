from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.model.common_base import CommonBase

# 定义基础类
class Base(DeclarativeBase):
    pass

class TableInfoModel(CommonBase):
    """元数据字段表"""
    __tablename__ = 't_table_info'

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment='主键id')
    name: Mapped[str] = mapped_column(String(128), comment='名称')
    type: Mapped[str] = mapped_column(String(64), comment='数据类型')
    role: Mapped[str] = mapped_column(String(32), comment='列类型(primary_key, foreign_key, measure, dimension)')
    examples: Mapped[list] = mapped_column(JSON, comment='数据示例')
    description: Mapped[str] = mapped_column(Text, comment='描述')
    alias: Mapped[list] = mapped_column(JSON, comment='别名')
    table_id: Mapped[str] = mapped_column(String(64), comment='表id')