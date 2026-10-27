# 【文件作用】
# 这个文件是"翻译器"（mapper 层），负责两种数据格式之间的映射（把一种格式的数据翻译成另一种格式）：
#   - TableInfoEntity（实体 entity）：程序内部传递数据用的"盒子"，类型宽松，允许 None
#   - TableInfoModel（模型 model）：数据库表 t_table_info 在代码里的"镜像"（用 SQLAlchemy 定义），管着真实的列
# 两个方向：to_entity（数据库读出来 → 代码盒子）、to_model（代码盒子 → 写进数据库）。
# 【注意】本项目只在 repository 层少数几个方法里调用它（读写大多直接操作 Model），所以它出场次数不多。

from dataclasses import asdict  # 导入 asdict：把 dataclass（数据盒子）一键转成普通字典

from app.entity.table_info_entity import TableInfoEntity  # 表信息实体：程序内部流转用的数据盒子
from app.model.table_info_model import TableInfoModel  # 数据库模型：和 t_table_info 表一一对应


class TableInfoMapper:  # 定义"表信息翻译器"类（里面全是转换方法，自己不放数据）
    '''
    表信息实体转换工具
    '''
    @staticmethod  # 静态方法：不用先创建对象，直接 TableInfoMapper.to_entity(...) 就能调用
    def to_entity(model:TableInfoModel)-> TableInfoEntity:  # 方向一：把数据库模型翻译成实体盒子
        return TableInfoEntity(  # 造一个新的实体对象并返回
            id=model.id,  # 主键 id 原样搬过去
            name=model.name,  # 表名
            description=model.description,  # 表描述
            role=model.role,  # 表角色（事实表 / 维度表）

        )  # 括号收尾；实体父类里的 del_flag / create_time 等字段没传，会用默认值

    @staticmethod  # 同样是静态方法
    def to_model(entity: TableInfoEntity) -> TableInfoModel:  # 方向二：把实体盒子翻译成数据库模型
        return TableInfoModel(**asdict(entity))  # asdict 先把实体拆成字典，** 再把字典的键值对展开成"字段名=值"的构造参数
