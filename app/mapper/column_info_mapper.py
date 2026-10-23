from app.entity.column_info_entity import ColumnInfoEntity
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMapper:
    """Entity(dataclass) 与 Model(ORM) 互转。不能用 asdict 处理 ORM 对象。"""

    @staticmethod
    def to_entity(model: ColumnInfoModel) -> ColumnInfoEntity:
        return ColumnInfoEntity(
            id=model.id,
            name=model.name,
            role=model.role,
            examples=model.examples,
            type=model.type,
            alias=model.alias,
            table_id=model.table_id,
            description=model.description,
            del_flag=model.del_flag,
            create_time=model.create_time,
            create_by=model.create_by,
            update_time=model.update_time,
            update_by=model.update_by,
        )

    @staticmethod
    def to_model(entity: ColumnInfoEntity) -> ColumnInfoModel:
        return ColumnInfoModel(
            id=entity.id,
            name=entity.name,
            role=entity.role,
            examples=entity.examples,
            type=entity.type,
            alias=entity.alias,
            table_id=entity.table_id,
            description=entity.description,
            del_flag=entity.del_flag,
            create_time=entity.create_time,
            create_by=entity.create_by,
            update_time=entity.update_time,
            update_by=entity.update_by,
        )
