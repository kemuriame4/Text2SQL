# 【文件作用】
# 这个文件是"翻译器"（mapper 层），负责字段信息两种数据格式之间的映射（把一种格式的数据翻译成另一种格式）：
#   - ColumnInfoEntity（实体 entity）：程序内部传递数据用的"盒子"
#   - ColumnInfoModel（模型 model）：数据库表 t_column_info 在代码里的"镜像"（用 SQLAlchemy 定义）
# 两个方向：to_entity（数据库读出来 → 代码盒子）、to_model（代码盒子 → 写进数据库）。
# 【注意】本项目只在 repository 层少数几个方法里调用它，出场次数不多。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from app.entity.column_info_entity import ColumnInfoEntity  # 字段信息实体：程序内部流转用的数据盒子
from app.model.column_info_model import ColumnInfoModel  # 数据库模型：和 t_column_info 表一一对应


class ColumnInfoMapper:  # 定义"字段信息翻译器"类
    '''
    字段信息实体转换工具
    '''
    @staticmethod  # 静态方法：直接用类名调用，不用创建对象
    def to_entity(model:ColumnInfoModel)-> ColumnInfoEntity:  # 方向一：把数据库模型翻译成实体盒子
        return ColumnInfoEntity(  # 造一个新的字段实体并返回
            id= model.id,  # 主键 id
            name=model.name,  # 字段名称
            description=model.description,  # 字段描述（这个字段是干什么的）
            type=model.type,  # 字段的数据类型（比如 int、varchar）
            alias=model.alias,  # 字段别名列表（数据库里存的是 JSON，取出来就是 list）
            examples=model.examples,  # 数据示例（存的是 JSON，取出来是 list，比如几个真实取值）
            role=model.role,  # 字段角色（主键 / 外键 / 度量 / 维度）
            table_id=model.table_id,  # 这个字段属于哪张表（表的 id）
            # 【注意】下面这行被注释掉了：模型里有 qdrant_id（向量库里的那条记录 id），但实体里没有这个字段，所以没搬过来
            # qdrant_id=model.qdrant_id,
        )  # 括号收尾

    @staticmethod  # 静态方法
    def to_model(entity: ColumnInfoEntity) -> ColumnInfoModel:  # 方向二：把实体盒子翻译成数据库模型
        return ColumnInfoModel(**asdict(entity))  # 转成字典再展开传参；实体字典里没有 qdrant_id 这个键，所以不会给它赋值
