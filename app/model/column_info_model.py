from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.model.common_base_model import CommonBaseModel


class ColumnInfoModel(CommonBaseModel):
    __tablename__ = 't_column_info'
    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment='主键id，格式: 表名.列名')
    name: Mapped[str] = mapped_column(String(128), comment='列名')
    type: Mapped[str] = mapped_column(String(64), comment='数据类型(来自dw库)')
    role: Mapped[str] = mapped_column(String(32), comment='角色 primary_key/foreign_key/dimension/measure')
    examples: Mapped[list] = mapped_column(JSON, comment='数据示例')
    description: Mapped[str] = mapped_column(Text, comment='描述')
    alias: Mapped[list] = mapped_column(JSON, comment='别名列表')
    table_id: Mapped[str] = mapped_column(String(64), comment='所属表id(t_table_info.id)')
