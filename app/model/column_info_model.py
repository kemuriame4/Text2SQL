from sqlalchemy import String, CHAR, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase


class ColumnInfoModel(CommonBase):
    __tablename__ = 't_column_info'
    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment='列编号')
    name: Mapped[str] = mapped_column(String(128), comment='列名称')
    type: Mapped[str] = mapped_column(String(64), comment='数据类型')
    role: Mapped[str] = mapped_column(CHAR(1), comment='列类型(primary_key,foreign_key,measure,dimension)')
    examples: Mapped[str] = mapped_column(JSON, comment='数据示例')
    description: Mapped[str] = mapped_column(Text, comment='列描述')
    alias: Mapped[str] = mapped_column(JSON, comment='列别名')
    table_id: Mapped[str] = mapped_column(String(64), comment='所属表编号')
