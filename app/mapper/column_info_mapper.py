from dataclasses import asdict

from app.entity.column_info_entity import ColumnInfoEntity
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMapper:
    '''
    表信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:ColumnInfoModel) -> ColumnInfoEntity:
        '''
        将数据实体转换为业务实体
        '''
        return ColumnInfoEntity(**asdict(model))

    @staticmethod
    def to_model(entity: ColumnInfoEntity) -> ColumnInfoModel:
        '''
        将业务实体转换为数据实体
        '''
        return ColumnInfoModel(**asdict(entity))