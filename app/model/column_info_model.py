from typing import Any

from sqlalchemy import String, CHAR, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase

class ColumnInfoModel(CommonBase):
    __tablename__ = 't_column_info'
    # id/name/table_id 的长度与 mysql/initmysql 里的 DDL 对齐（DDL 是 varchar(64)）
    id:Mapped[str] = mapped_column(String(64),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(128),nullable=True,comment='名称')
    role:Mapped[str | None] = mapped_column(String(32),nullable=True,comment='列类型(primary_key,foreign_key,measure,dimension)')
    description:Mapped[str | None] = mapped_column(Text,nullable=True,comment='描述')
    # examples / alias 在数据库里是 json 列，Python 侧的真实类型是 list，注解写 str 是错的
    examples:Mapped[list[Any] | None] = mapped_column(JSON,nullable=True,comment='数据示例')
    type:Mapped[str | None] = mapped_column(String(64),nullable=True,comment='数据类型')
    alias:Mapped[list[str] | None] = mapped_column(JSON,nullable=True,comment='别名')
    table_id:Mapped[str | None] = mapped_column(String(64),nullable=True,comment='表id')



