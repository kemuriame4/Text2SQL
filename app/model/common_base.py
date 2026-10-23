from datetime import  datetime
from sqlalchemy import  String,CHAR,DateTime

from sqlalchemy.orm import  DeclarativeBase,Mapped,mapped_column

class CommonBase(DeclarativeBase):
    '''
        所有数据实体的公共基类（mixin 列，会被子类继承）
        注意：建表 SQL（mysql/initmysql）里这些字段都是 DEFAULT NULL，
              所以这里必须写 nullable=True，否则 entity 里没赋值的字段会以 NULL 插入而报错。
        '''

    del_flag:Mapped[str| None] = mapped_column(CHAR(1),nullable = True,default='0',comment='是否删除 0 未删除  1 已删除')
    create_time: Mapped[datetime | None] = mapped_column(DateTime,nullable=True,comment='创建时间')
    create_by: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='创建者')
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='修改时间')
    update_by: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='修改者')