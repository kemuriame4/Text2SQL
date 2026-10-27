# 【文件作用】
# 这个文件是"翻译器"（mapper 层），负责"字段 ↔ 指标"关联关系两种数据格式之间的映射（把一种格式的数据翻译成另一种格式）：
#   - ColumnMetricEntity（实体 entity）：程序内部传递数据用的"盒子"
#   - ColumnMetricModel（模型 model）：数据库表 t_column_metric 在代码里的"镜像"（一张多对多关联表）
# 两个方向：to_entity（数据库读出来 → 代码盒子）、to_model（代码盒子 → 写进数据库）。
# 【注意】本项目只在 repository 层少数几个方法里调用它，出场次数不多。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from app.entity.column_metric_entity import ColumnMetricEntity  # 关联关系实体
from app.model.column_metric_model import ColumnMetricModel  # 数据库模型：和 t_column_metric 表一一对应


class ColumnMetricMapper:  # 定义"字段-指标关联翻译器"类
    # 【注意】下面这段文档注释是复制来的，写成了"字段信息"，本类实际处理的是"字段与指标的关联关系"（不改动原字符串）
    '''
    字段信息实体转换工具
    '''
    @staticmethod  # 静态方法：直接用类名调用，不用创建对象
    def to_entity(model:ColumnMetricModel)-> ColumnMetricEntity:  # 方向一：把数据库模型翻译成实体盒子
        return ColumnMetricEntity(  # 造一个新的关联实体并返回
            column_id= model.column_id,  # 字段 id（这条关联里的一方）
            metric_id=model.metric_id,  # 指标 id（这条关联里的另一方）
        )  # 括号收尾

    @staticmethod  # 静态方法
    def to_model(entity: ColumnMetricEntity) -> ColumnMetricModel:  # 方向二：把实体盒子翻译成数据库模型
        return ColumnMetricModel(**asdict(entity))  # asdict 把实体拆成字典，** 再按"字段名=值"展开成构造参数
