from sqlalchemy import String, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase


class TableInfoModel(CommonBase):
    __tablename__ = 't_table_info'
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(64),comment='名称')
    role:Mapped[str] = mapped_column(CHAR(1),comment='角色 0:维度表  1 事实表 ')
    description:Mapped[str] = mapped_column(String(255),comment='描述')


