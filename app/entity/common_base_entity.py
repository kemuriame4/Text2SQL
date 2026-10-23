from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class CommonBaseEntity:
    del_flag: str = '0'
    create_time: datetime | None = field(default=None)
    create_by: str = ''
    update_time: datetime | None = None
    update_by: str = ''
