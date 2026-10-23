from dataclasses import dataclass, field

from app.entity.common_base_entity import CommonBaseEntity


@dataclass
class ColumnInfoEntity(CommonBaseEntity):
    id: str
    name: str
    type: str
    role: str
    description: str
    table_id: str
    examples: list = field(default_factory=list)
    alias: list = field(default_factory=list)
