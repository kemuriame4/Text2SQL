from dataclasses import asdict

from app.entity.table_info_entity import TableInfoEntity
from app.model.table_info_model import TableInfoModel


class TableInfoMapper:
    '''
    表信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:TableInfoModel) -> TableInfoEntity:
        '''
        将数据实体转换为业务实体
        '''
        return TableInfoEntity(**asdict(model))

    @staticmethod
    def to_model(entity: TableInfoEntity) -> TableInfoModel:
        '''
        将业务实体转换为数据实体
        '''
        return TableInfoModel(**asdict(entity))