from pydantic.dataclasses import dataclass

from app.entity.common_entity import CommonBaseEntity


@dataclass
class ColumnMetricEntity(CommonBaseEntity):

    column_id:str | None = None
    metric_id:str | None = None
