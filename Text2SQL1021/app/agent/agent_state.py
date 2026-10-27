# 【文件作用】
# 这个文件定义"图里流动的数据长什么样"，也就是状态（State）。
# 状态是节点之间传递的"共享笔记本"：上一个节点写进去的东西，下一个节点能读到；
# 这里只写字段名和类型，不存真实数据（真实数据在每次运行时由 LangGraph 帮你塞进去）。
# TypedDict（一种用来规定"字典里该有哪些键、每个键是什么类型"的写法，运行时它就是普通 dict）
from typing import TypedDict

# 三个实体类（用 @dataclass 写的"数据小盒子"），下面 AgentState 的字段类型会直接引用它们
from app.entity.column_info_entity import ColumnInfoEntity  # 字段信息
from app.entity.metric_info_entity import MetricInfoEntity  # 指标信息
from app.entity.value_info import ValueInfo  # 字段里的具体取值


# 字段（表里的一列）的精简版状态：只保留后面拼 prompt 真正需要的字段
class ColumnInfoState(TypedDict):
    name: str  # 字段名，例如 order_amount
    type: str  # 字段类型，例如 varchar、int
    role: str  # 字段角色，例如是不是主键/外键
    examples: list  # 这个字段里出现过的真实取值示例，帮助大模型理解字段含义
    description: str  # 字段的业务说明，例如"订单金额"
    alias: list[str]  # 字段的别名/同义词，例如 ["销售额", "营收"]

# 表的精简版状态：一张表 + 它包含的所有字段
class TableInfoState(TypedDict):
    name: str  # 表名，例如 dwd_order
    role: str  # 表的角色，例如事实表、维度表
    description: str  # 表的业务说明
    columns: list[ColumnInfoState]  # 这张表里的字段清单（每个元素都是上面的 ColumnInfoState）

# 指标的精简版状态：指标就是"销售额""订单量"这类业务口径
class MetricInfoState(TypedDict):
    name: str  # 指标名，例如 销售额
    description: str  # 指标的业务说明（怎么算出来的）
    retrieval_columns: list[str]  # 这个指标要用到的字段 id 列表（注意：实体里叫 relevant_columns，这里换了个名字）
    alias: list[str]  # 指标的别名/同义词



# AgentState（整张图共用的状态）：所有节点读写的就是这一份数据
class AgentState(TypedDict):
    question: str  # 用户输入的原始问题，例如"给我查询今年各地区第一季度的销售额"
    keywords: list[str]  # keywords_ext 节点切出来的关键词（含原始问题本身）
    # 【注意】is_end 定义了，但整个工程里没有任何节点读它或写它，属于"预留但没用上"的字段。
    # 想用它做"提前结束"需要在节点里返回 {'is_end': True} 并配 conditional_edges（条件边）才生效。
    is_end: bool  # 标记是否已经结束（目前未使用）
    retrieval_columns: list[ColumnInfoEntity]  # 字段召回结果，由 retrievalColumns 节点写入
    retrieval_metrics: list[MetricInfoEntity]  # 指标召回结果，由 retrievalMetric 节点写入
    retrieval_values: list[ValueInfo]  # 具体取值召回结果，由 retrievalValue 节点写入

    # 下面两个字段是 mergeRetrieval 节点"加工后"的最终产物，结构更贴近拼 prompt 的需要
    table_infos: list[TableInfoState]  # 整理好的表 + 字段结构
    metric_infos: list[MetricInfoState]  # 整理好的指标结构
