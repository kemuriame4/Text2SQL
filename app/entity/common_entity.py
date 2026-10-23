from dataclasses import field
from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class CommonBaseEntity:
    del_flag: str | None = '0'
    create_time: datetime | None = field(default_factory=datetime.now)
    create_by: str | None = None
    update_time: datetime | None = field(default_factory=datetime.now)
    update_by: str | None = None
