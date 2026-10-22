from dataclasses import dataclass

from app.entity.common_base_entity import CommonBaseEntity


@dataclass
class TableInfoEntity(CommonBaseEntity):
    id: str
    name: str
    role: str
    description: str
