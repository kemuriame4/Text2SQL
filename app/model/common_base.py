from datetime import datetime
from xmlrpc.client import DateTime

from sqlalchemy import String,CHAR,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class CommonBase(DeclarativeBase):
    del_flag:Mapped[str] = mapped_column(CHAR(1),comment='是否删除 0未删除  1已删除')
    create_time:Mapped[datetime] = mapped_column(DateTime,comment='创建时间')
    create_by:Mapped[str] = mapped_column(String(64),comment='创建者')
    update_time:Mapped[datetime] = mapped_column(DateTime,comment='修改时间')
    update_by:Mapped[str] = mapped_column(String(64),comment='修改者')


