from datetime import datetime
from dataclasses import dataclass

@dataclass
class CommonBaseEntity:
    del_flag:str | None = '0'
    create_time:datetime | None = datetime.now()
    create_by:str | None = None
    update_time:datetime | None = datetime.now()
    update_by:str | None = None