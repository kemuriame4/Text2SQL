# 【文件作用】
# 这个文件定义"一个字段的取值示例"在代码里长什么样（entity 盒子），用来把真实数据值带给大模型参考。
# 它只负责装数据，不连数据库。
from dataclasses import dataclass  # 导入标准库的 dataclass（Python 自带的"纯数据盒子"写法）


@dataclass  # 套上 dataclass 装饰器：自动生成初始化方法
class ValueInfo:  # 定义"取值信息"盒子类，装一条字段的示例值
    id: str  # 主键 id：唯一标识这条取值记录（必填，没有默认值）
    value: str  # 具体的值：比如某个字段真实出现过的"北京"（必填）
    column_id: str  # 所属字段的 id：这个值属于哪一列（必填）
