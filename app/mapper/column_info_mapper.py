from dataclasses import asdict

from app.entity.column_info_entity import ColumnInfoEntity
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMapper:
    '''
    字段信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:ColumnInfoModel)-> ColumnInfoEntity:
        return ColumnInfoEntity(**asdict(model))

    @staticmethod
    def to_model(entity: ColumnInfoEntity) -> ColumnInfoModel:
        return ColumnInfoModel(**asdict(entity))