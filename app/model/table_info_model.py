from sqlalchemy import String, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase


class TableInfoModel(CommonBase):
    __tablename__ = 't_table_info'
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str | None] = mapped_column(String(64),nullable=True,comment='名称')
    # role 存的是 dim / fact 这类字符串，建表 SQL 里千万别用 char(1)，会被截断
    role:Mapped[str | None] = mapped_column(String(32),nullable=True,comment='角色 dim:维度表  fact:事实表')
    description:Mapped[str | None] = mapped_column(String(255),nullable=True,comment='描述')


