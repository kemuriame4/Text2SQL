from dataclasses import asdict

from app.entity.table_info_entity import TableInfoEntity
from app.model.table_info_model import TableInfoModel


class TableInfoMapper:
    '''
    字段信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:TableInfoModel)-> TableInfoEntity:
        return TableInfoEntity(**asdict(model))

    @staticmethod
    def to_model(entity: TableInfoEntity) -> TableInfoModel:
        return TableInfoModel(**asdict(entity))