from dataclasses import asdict

from app.entity.column_info_entity import ColumnInfoEntity
from app.model.column_info_model import ColumnInfoModel

class ColumnInfoMapper:
    '''
        字段信息实体转换工具

    '''
    @staticmethod
    def to_entity(model:ColumnInfoModel)-> ColumnInfoEntity:
        return ColumnInfoEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            typr=model.type,
            alias=model.alias,
            examples = model.examples,
            role=model.role,
            table_id=model.table_id
        )

    @staticmethod
    def to_model(entity:ColumnInfoEntity)-> ColumnInfoModel:
        return ColumnInfoModel(**asdict(entity))