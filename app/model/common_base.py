"""ORM 基类：所有表都带的 5 个公共列（逻辑删除 + 审计字段）。"""
from datetime import datetime
from sqlalchemy import String, CHAR, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CommonBase(DeclarativeBase):
    """
    做什么：SQLAlchemy 2.x 的声明式基类，被各 model 继承，让每张表自动拥有这 5 个公共列。
    字段：
    del_flag (Mapped[str])：逻辑删除标记，'0' 未删除、'1' 已删除；CHAR(1)。
    create_time (Mapped[datetime])：创建时间。
    create_by (Mapped[str])：创建者。
    update_time (Mapped[datetime])：修改时间。
    update_by (Mapped[str])：修改者。
    注意：这 5 个列在这里只声明结构，没有默认值；新增数据时不赋值，落库后都是 NULL。
    """
    del_flag: Mapped[str] = mapped_column(CHAR(1), comment='是否删除 0 未删除  1 已删除')
    create_time: Mapped[datetime] = mapped_column(DateTime, comment='创建时间')
    create_by: Mapped[str] = mapped_column(String(64), comment='创建者')
    update_time: Mapped[datetime] = mapped_column(DateTime, comment='修改时间')
    update_by: Mapped[str] = mapped_column(String(64), comment='修改者')
