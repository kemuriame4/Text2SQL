from dataclasses import asdict
from APP.entity.table_info_entity import TableInfoEntity
from APP.model.table_info_model import TableInfoModel

class TableInfoMapper:
    '''
    表信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:TableInfoModel) -> TableInfoEntity:
        return TableInfoEntity(
            id = model.id ,
            name = model.name ,
            description = model.description ,
            role = model.role ,
        )

    @staticmethod
    def to_model(model:TableInfoModel) -> TableInfoModel:
        return TableInfoModel(**asdict(entity))