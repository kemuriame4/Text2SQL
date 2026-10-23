"""字段信息的 ORM 映射，对应元数据库里的 t_column_info。"""
from sqlalchemy import String, CHAR, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base import CommonBase

class ColumnInfoModel(CommonBase):
    """t_column_info 的一行 = 一个字段的元数据，是三库（MySQL / Qdrant / ES）的共同源头。"""
    __tablename__ = 't_column_info'
    # 字段：
    # id (Mapped[str])：主键，实际存的是"表名.字段名"（如 dim_region.region_name）。
    # name (Mapped[str])：字段名，例如 region_name。
    # role (Mapped[str])：字段角色，primary_key / foreign_key / measure / dimension 之一。
    # description (Mapped[str])：字段中文说明。
    # examples (Mapped[str])：数据示例，JSON 数组；类型标注写的是 str，实际存 list。
    # type (Mapped[str])：数据库里的真实类型，如 varchar(64)，由数仓 SHOW COLUMNS 得到。
    # alias (Mapped[str])：字段别名，JSON 数组；类型标注写的是 str，实际存 list。
    # table_id (Mapped[str])：所属表的 id，取值等于 t_table_info.id。
    # del_flag / create_time / create_by / update_time / update_by：继承自 CommonBase。
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(64),comment='名称')
    role:Mapped[str] = mapped_column(String(32),comment='列类型(primary_key,foreign_key,measure,dimension)')
    description:Mapped[str] = mapped_column(Text,comment='描述')
    examples:Mapped[str] = mapped_column(JSON,comment='数据示例')
    type:Mapped[str] = mapped_column(String(64),comment='数据类型')
    alias:Mapped[str] = mapped_column(JSON,comment='别名')
    table_id:Mapped[str] = mapped_column(String(32),comment='表id')



