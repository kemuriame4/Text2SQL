"""元数据配置结构：描述 conf/meta_config.yaml 里"管哪些表、哪些字段、哪些指标"。"""
from pydantic.dataclasses import dataclass


@dataclass
class ColumnConfig():
    """yaml 里一个字段（列）的声明。"""
    # 字段：
    # name (str)：数据仓库里的真实列名，例如 region_name。
    # role (str)：列类型，取值 primary_key / foreign_key / measure / dimension。
    # description (str)：列的中文说明，会写进元数据库。
    # alias (list[str])：用户可能说出的同义词，例如 [地区, 区域, 大区]。
    # sync (bool)：该列的取值是否要同步到 ES；true 才会进 ES。
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool

@dataclass
class TableConfig():
    """yaml 里一张表的声明，字段列表是嵌套的 ColumnConfig。"""
    # 字段：
    # name (str)：数据仓库里的真实表名，同时也是元数据库里的表主键。
    # role (str)：表角色，dim（维度表）或 fact（事实表）。
    # description (str)：表的中文说明。
    # columns (list[ColumnConfig])：这张表下的所有字段声明。
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]

@dataclass
class MetricConfig:
    """yaml 里一个业务指标的声明。"""
    # 字段：
    # name (str)：指标名，例如 GMV、AOV。
    # description (str)：指标的业务口径说明。
    # relevant_columns (list[str])：算出该指标需要的字段，格式是 "表名.字段名"。
    # alias (list[str])：用户可能说出的别名，例如 [成交总额, 订单总额]。
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

@dataclass
class MetaConfig:
    """整份 meta_config.yaml 的结构，顶层只有两张清单。"""
    # 字段：
    # tables (list[TableConfig])：要纳入管理的表清单。
    # metrics (list[MetricConfig])：要纳入管理的指标清单。
    tables: list[TableConfig]
    metrics: list[MetricConfig]

