from dataclasses import asdict

from personal.entity.info_entity import TableInfoEntity, MetricInfoEntity
from personal.model.info_model import TableInfoModel, MetricInfoModel


class TableInfoMapper:
    """
    表信息实体转换工具
    """

    @staticmethod
    def to_entity(model: TableInfoModel) -> TableInfoEntity:
        return TableInfoEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            role=model.role,
        )

    @staticmethod
    def to_model(entity: TableInfoEntity) -> TableInfoModel:
        return TableInfoModel(**asdict(entity))


class MetricInfoMapper:
    """
    指标信息实体转换工具
    """

    @staticmethod
    def to_entity(model: MetricInfoModel) -> MetricInfoEntity:
        return MetricInfoEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            alias=model.alias,
            relevant_columns=model.relevant_columns,
        )

    @staticmethod
    def to_model(entity: MetricInfoEntity) -> MetricInfoModel:
        return MetricInfoModel(**asdict(entity))
