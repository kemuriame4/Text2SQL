"""表信息转换器：在 ORM 模型 TableInfoModel 与业务实体 TableInfoEntity 之间互换。"""
from dataclasses import asdict

from app.entity.table_info_entity import TableInfoEntity
from app.model.table_info_model import TableInfoModel


class TableInfoMapper:
    '''
    表信息实体转换工具
    '''
    @staticmethod
    def to_entity(model:TableInfoModel)-> TableInfoEntity:
        """
        做什么：把从数据库查出来的 ORM 模型转成业务实体。
        参数：
        model (TableInfoModel)：数据库查询返回的一行，对应 t_table_info 的一条记录。
        返回：
        TableInfoEntity：只填了 id / name / description / role 四个字段；
        其余字段（del_flag、create_time 等）用实体类的默认值。
        注意：这里是手工逐字段赋值，数据库里已有的 del_flag / 时间字段被丢掉了，
        拿到的实体再转回 model 时，这些字段会变成默认值。目前没有逆向使用，所以不影响运行。
        """
        return TableInfoEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            role=model.role,

        )

    @staticmethod
    def to_model(entity: TableInfoEntity) -> TableInfoModel:
        """
        做什么：把业务实体展开成字段字典，再构造 ORM 模型，用于新增。
        参数：
        entity (TableInfoEntity)：由 service 组装好的表信息实体。
        返回：
        TableInfoModel：还没加入 session 的 ORM 对象，需要 repository 再 add。
        注意：asdict 会把实体的所有字段（含继承来的 5 个公共字段）都塞进构造参数，
        所以实体字段必须和模型列一一对应，否则这里直接抛 TypeError。
        """
        return TableInfoModel(**asdict(entity))
