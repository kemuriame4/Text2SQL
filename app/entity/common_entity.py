import datetime
from dataclasses import dataclass


@dataclass
class CommonBaseEntity:
    del_flag: str
    create_time: datetime
    create_by: str
    update_time: datetime
    update_by: str