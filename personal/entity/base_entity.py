from datetime import datetime
from dataclasses import dataclass


@dataclass
class BaseEntity:
    del_flag: str | None = "0"
    create_time: datetime | None = datetime.now()
    create_by: str | None = None
    update_time: datetime | None = datetime.now()
    update_by: str | None = None


@dataclass
class ValueInfo:
    """
    id: 主键ID
    value: 值
    column_id: 字段ID
    """

    id: str
    value: str
    column_id: str
