from pydantic.dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class MetricInfoEntity(CommonBaseEntity):

    id:str | None = None
    name:str | None = None
    description:str | None = None
    alias: list[str] | None = None
    relevant_columns: list[str] | None = None