from pydantic.dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class TableInfoEntity(CommonBaseEntity):
    """元数据表信息"""
    id: str | None = None
    name: str | None = None
    role: str | None = None
    description: str | None = None
