from dataclasses import asdict

from app.entity.column_metric_entity import ColumnMetricEntity
from app.model.column_metric_model import ColumnMetricModel


class ColumnMetricMapper:
    '''
    字段信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:ColumnMetricModel)-> ColumnMetricEntity:
        return ColumnMetricEntity(
            column_id= model.column_id,
            metric_id=model.metric_id,
        )

    @staticmethod
    def to_model(entity: ColumnMetricEntity) -> ColumnMetricModel:
        return ColumnMetricModel(**asdict(entity))