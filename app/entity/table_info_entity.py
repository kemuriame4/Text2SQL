from app.model.common_base import CommonBase

class TableInfoEntity(CommonBase):
    """元数据字段表"""
    __tablename__ = 't_table_info'
    '''
    id  主键id
    name: 表名称
    role : 表角色   事实表、维度表
    description 表描述
    '''
    id:str
    name:str
    role:str
    description:str