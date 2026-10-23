from sqlalchemy import String,CHAR,Text,JSON
from sqlalchemy.orm import Mapped,mapped_column

from app.model.common_base import CommonBase

class ColumnInfoModel(CommonBase):
    __tablename__ = 't_column_info'
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')
    name:Mapped[str] = mapped_column(String(64),comment='名称')
    role:Mapped[str] = mapped_column(String(32),comment='列类型(primary_key,foreign_key,measure,dimension)')
    description:Mapped[str] = mapped_column(Text,comment='描述')
    examples:Mapped[str] = mapped_column(JSON,comment='数据示例')
    type:Mapped[str] = mapped_column(String(64),comment='数据类型')
    alias:Mapped[str] = mapped_column(JSON,comment='别名')
    table_id:Mapped[str] = mapped_column(String(32),comment='表id')


