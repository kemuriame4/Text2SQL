from app.entity.table_info_entity import TableInfoEntity
from app.model.table_info_model import TableInfoModel


class TableInfoMapper:
    """Entity(dataclass) 与 Model(ORM) 互转。不能用 asdict 处理 ORM 对象。"""

    @staticmethod
    def to_entity(model: TableInfoModel) -> TableInfoEntity:
        return TableInfoEntity(
            id=model.id,
            name=model.name,
            role=model.role,
            description=model.description,
            del_flag=model.del_flag,
            create_time=model.create_time,
            create_by=model.create_by,
            update_time=model.update_time,
            update_by=model.update_by,
        )

    @staticmethod
    def to_model(entity: TableInfoEntity) -> TableInfoModel:
        return TableInfoModel(
            id=entity.id,
            name=entity.name,
            role=entity.role,
            description=entity.description,
            del_flag=entity.del_flag,
            create_time=entity.create_time,
            create_by=entity.create_by,
            update_time=entity.update_time,
            update_by=entity.update_by,
        )
