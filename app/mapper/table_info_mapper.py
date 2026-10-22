from dataclasses import asdict

from app.entity.table_info_entity import TableInfoEntity
from app.model.table_info_model import TableInfoModel


class TableInfoMapper:
    @staticmethod
    def to_entity(model:TableInfoModel):
        return TableInfoEntity(
            **asdict(model)
        )
    @staticmethod
    def to_model(entity:TableInfoEntity):
        return TableInfoModel(
            **asdict(entity)
        )