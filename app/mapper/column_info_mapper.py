"""字段信息转换器：在 ORM 模型 ColumnInfoModel 与业务实体 ColumnInfoEntity 之间互换。"""
from dataclasses import asdict

from app.entity.column_info_entity import ColumnInfoEntity
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMapper:
    '''
    字段信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:ColumnInfoModel)-> ColumnInfoEntity:
        """
        做什么：把从数据库查出来的字段记录转成业务实体。
        参数：
        model (ColumnInfoModel)：数据库查询返回的一行，对应 t_column_info 的一条记录。
        返回：
        ColumnInfoEntity：填了 id / name / description / type / alias / examples / role / table_id；
        公共字段（del_flag 等）用实体默认值。
        注意：alias 和 examples 在模型里声明成 JSON，读出来已经是 list，不需要再 json.loads。
        """
        return ColumnInfoEntity(
            id= model.id,
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
        """
        做什么：把字段实体展开成字段字典，再构造 ORM 模型，用于新增。
        参数：
        entity (ColumnInfoEntity)：由 service 组装好的字段实体。
        返回：
        ColumnInfoModel：还没加入 session 的 ORM 对象。
        注意：examples 里如果混进了 Decimal、datetime 这类非 JSON 原生类型，
        写入 JSON 列时会序列化失败，需要在调用前先转成 str。
        """
        return ColumnInfoModel(**asdict(entity))
