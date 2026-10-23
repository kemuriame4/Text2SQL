from sqlalchemy.orm import Mapped ,mapped_column
from sqlalchemy.testing.schema import mapped_column

from APP.model.common_base import CommonBase
from sqlalchemy import String

class TableInfoModel(CommonBase):
    __tablename__ = 't_table_info'
    id:Mapped[str] = mapped_column(String(32))

