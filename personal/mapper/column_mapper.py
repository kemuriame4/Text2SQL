from dataclasses import asdict

from personal.model.column_model import ColumnInfoModel, ColumnMetricModel
from personal.entity.column_entity import ColumnInfoEntity, ColumnMetricEntity


class ColumnInfoMapper:
    """
    字段信息实体转换工具
    """

    @staticmethod
    def to_entity(model: ColumnInfoModel) -> ColumnInfoEntity:
        return ColumnInfoEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            type=model.type,
            alias=model.alias,
            examples=model.examples,
            role=model.role,
            table_id=model.table_id,
            # qdrant_id=model.qdrant_id,
        )

    @staticmethod
    def to_model(entity: ColumnInfoEntity) -> ColumnInfoModel:
        return ColumnInfoModel(**asdict(entity))


class ColumnMetricMapper:
    """
    字段度量关系实体转换工具
    """

    @staticmethod
    def to_entity(model: ColumnMetricModel) -> ColumnMetricEntity:
        return ColumnMetricEntity(
            column_id=model.column_id,
            metric_id=model.metric_id,
        )

    @staticmethod
    def to_model(entity: ColumnMetricEntity) -> ColumnMetricModel:
        return ColumnMetricModel(**asdict(entity))
