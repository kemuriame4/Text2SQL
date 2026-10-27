# 【文件作用】
# 这个文件定义所有数据库 model（数据库表在代码里的镜像）共用的公共字段：是否删除、创建/修改的时间与人。
# 它用 SQLAlchemy 的 ORM 写法，子类继承后会自动拥有这些列；代码各层之间传数据用 app/entity/common_entity.py。
from datetime import datetime  # 导入 datetime（日期时间类型，对应数据库的 datetime）
from sqlalchemy import String, CHAR, DateTime  # 从 SQLAlchemy 导入列类型：String 变长字符串、CHAR 定长字符串、DateTime 日期时间
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # 导入 ORM 三件套：DeclarativeBase 声明式基类、Mapped 标注字段的 Python 类型、mapped_column 定义数据库列（相当于新版 Column，说明这个字段对应数据库里的哪一列、什么类型）


class CommonBase(DeclarativeBase):  # 定义公共 model 基类，继承 DeclarativeBase（SQLAlchemy 的声明式基类，所有表都从它派生）
    del_flag: Mapped[str] = mapped_column(CHAR(1), comment='是否删除 0 未删除  1 已删除')  # 是否删除：CHAR(1) 一位字符，'0' 未删除、'1' 已删除（软删除标记）
    create_time: Mapped[datetime] = mapped_column(DateTime, comment='创建时间')  # 创建时间：什么时候插入的这条数据
    create_by: Mapped[str] = mapped_column(String(64), comment='创建者')  # 创建者：谁插入的这条数据，最长 64 字符
    update_time: Mapped[datetime] = mapped_column(DateTime, comment='修改时间')  # 修改时间：最后一次改动的时间
    update_by: Mapped[str] = mapped_column(String(64), comment='修改者')  # 修改者：谁最后改的这条数据，最长 64 字符
