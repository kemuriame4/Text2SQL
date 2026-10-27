# 【文件作用】
# 这个文件是"翻译器"（mapper 层），负责指标信息两种数据格式之间的映射（把一种格式的数据翻译成另一种格式）：
#   - MetricInfoEntity（实体 entity）：程序内部传递数据用的"盒子"
#   - MetricInfoModel（模型 model）：数据库表 t_metric_info 在代码里的"镜像"（用 SQLAlchemy 定义）
# 两个方向：to_entity（数据库读出来 → 代码盒子）、to_model（代码盒子 → 写进数据库）。
# 【注意】本项目只在 repository 层少数几个方法里调用它，出场次数不多。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from app.entity.metric_info_entity import MetricInfoEntity  # 指标信息实体（指标 = 可统计的业务口径，如"销售额"）
from app.model.metric_info_model import MetricInfoModel  # 数据库模型：和 t_metric_info 表一一对应


class MetricInfoMapper:  # 定义"指标信息翻译器"类
    # 【注意】下面这段文档注释是从字段转换器复制来的，写成了"字段信息"，本类实际处理的是"指标信息"（不改动原字符串）
    '''
    字段信息实体转换工具
    '''
    @staticmethod  # 静态方法：直接用类名调用，不用创建对象
    def to_entity(model:MetricInfoModel)-> MetricInfoEntity:  # 方向一：把数据库模型翻译成实体盒子
        return MetricInfoEntity(  # 造一个新的指标实体并返回
            id= model.id,  # 主键 id
            name=model.name,  # 指标名称（比如"销售额"）
            description=model.description,  # 指标描述（这个指标怎么算的、什么口径）
            alias=model.alias,  # 指标别名列表（存 JSON，取出来是 list，比如"营收"）
            relevant_columns=model.relevant_columns,  # 关联的字段列表（算这个指标要用到哪些字段，存 JSON）
        )  # 括号收尾

    @staticmethod  # 静态方法
    def to_model(entity: MetricInfoEntity) -> MetricInfoModel:  # 方向二：把实体盒子翻译成数据库模型
        return MetricInfoModel(**asdict(entity))  # asdict 把实体拆成字典，** 再按"字段名=值"展开成构造参数
