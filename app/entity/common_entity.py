
from dataclasses import dataclass
from datetime import datetime



@dataclass
class CommonEntity():
    del_flag: str
    create_time: datetime
    create_by: str
    update_time: datetime
    update_by: str