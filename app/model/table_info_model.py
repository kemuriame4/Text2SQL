"""表信息的 ORM 映射，对应元数据库里的 t_table_info。"""
from sqlalchemy import String, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase


class TableInfoModel(CommonBase):
    """t_table_info 的一张表 = 一条记录，描述"有这张表、它是什么角色"。"""
    __tablename__ = 't_table_info'
    # 字段：
    # id (Mapped[str])：主键，实际存的是表名（如 dim_region），String(32)。
    # name (Mapped[str])：表名称，目前和 id 取值一样。
    # role (Mapped[str])：表角色。注释写的是 0/1，但代码实际写入的是 dim / fact。
    # description (Mapped[str])：表的中文说明，String(255)。
    # del_flag / create_time / create_by / update_time / update_by：继承自 CommonBase。
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(64),comment='名称')
    role:Mapped[str] = mapped_column(String(64),comment='角色 0:维度表  1 事实表 ')
    description:Mapped[str] = mapped_column(String(255),comment='描述')


