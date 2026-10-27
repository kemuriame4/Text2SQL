# ============================================================================
# 【文件说明】app/conf/meta_config.py —— 元数据配置的"模板类"（内层）
# 作用：规定 conf/meta_config.yaml（人工写的表结构说明）里应该有哪些字段。
# 结构：总配置 MetaConfig 分两块 —— tables（表清单）、metrics（指标清单）；
#       每张表 TableConfig 有 name/role/description/columns；
#       每个字段 ColumnConfig 有 name/role/description/alias/sync；
#       每个指标 MetricConfig 有 name/description/relevant_columns/alias。
# 怎么用：app/service/meta_service.py 里 load_config(meta_config.yaml, MetaConfig)，把值填进来。
# 【注意】这里用的是 pydantic 的 dataclass（pydantic 会顺带做类型校验），
#         和 app_config.py 用标准库 dataclasses 不一致。
# ============================================================================
from pydantic.dataclasses import dataclass  # 从 pydantic 导入 dataclass；比标准库版本多一层类型校验


@dataclass  # 装饰器：把类变成"数据盒子"（pydantic 版还会校验类型）
class ColumnConfig():  # 描述"一个字段"的配置
    name: str  # 字段名（必须和数仓里真实的列名一致，拼 SQL 时直接用）
    role: str  # 字段角色：primary_key 主键 / foreign_key 外键 / measure 度量 / dimension 维度
    description: str  # 字段的中文说明，给大模型看，帮它理解这一列是什么
    alias: list[str]  # 别名/同义词列表（用户说"销售额"或"收入"都可能指同一列）
    sync: bool  # 这个字段的"值"要不要同步进 ES 做全文检索（true 同步，false 不同步）

@dataclass  # 同样当数据盒子处理
class TableConfig():  # 描述"一张表"的配置
    name: str  # 表名（数仓里的真实表名）
    role: str  # 表的角色：dim 维度表 / fact 事实表
    description: str  # 表的中文说明
    columns: list[ColumnConfig]  # 这张表里所有字段的配置，是一个列表

@dataclass  # 同样当数据盒子处理
class MetricConfig:  # 描述"一个指标"的配置（指标 = 业务上常算的一个数，比如 GMV）
    name: str  # 指标名，例如 GMV、AOV
    description: str  # 指标的文字解释
    relevant_columns: list[str]  # 算这个指标要用到哪些字段，写成"表名.字段名"
    alias: list[str]  # 指标的别名，用户口语里可能这么说

@dataclass  # 同样当数据盒子处理
class MetaConfig:  # 元数据总配置：整个 YAML 的顶层就两块
    tables: list[TableConfig]  # 所有表的配置
    metrics: list[MetricConfig]  # 所有指标的配置

