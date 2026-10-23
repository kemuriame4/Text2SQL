from dataclasses import asdict

from app.entity.metric_info_entity import MetricInfoEntity
from app.model.metric_info_model import MetricInfoModel


class MetricInfoMapper:
    '''
    字段信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:MetricInfoModel)-> MetricInfoEntity:
        return MetricInfoEntity(
            id= model.id,
            name=model.name,
            description=model.description,
            alias=model.alias,
            relevant_columns=model.relevant_columns,
        )

    @staticmethod
    def to_model(entity: MetricInfoEntity) -> MetricInfoModel:
        return MetricInfoModel(**asdict(entity))