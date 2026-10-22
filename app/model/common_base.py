
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import CHAR, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


@dataclass
class CommonBase():
    del_flag: Mapped[str] = mapped_column(CHAR(1), default='0', comment='删除标志(0:正常,1:已删除)')
    create_time: Mapped[datetime] = mapped_column(DateTime, comment='创建时间')
    create_by: Mapped[str] = mapped_column(String(64), comment='创建者')
    update_time: Mapped[datetime] = mapped_column(DateTime, comment='修改时间')
    update_by: Mapped[str] = mapped_column(String(255), comment='修改者')



