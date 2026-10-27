# 【文件作用】
# 这个文件定义"运行时上下文"（Runtime Context）：节点执行时能拿到的外部资源。
# 和 AgentState 的区别：State 装"跟问题有关、会变化的数据"；Context 装"数据库/向量库连接"这类不随问题变化的东西。
# 好处：连接只建一次，由外部在调用时注入（传给 astream 的 context 参数），节点里直接取用，不用反复连接。
# TypedDict（一种用来规定"字典里该有哪些键、每个键是什么类型"的写法，运行时它就是普通 dict）
from typing import TypedDict

# 下面导入的都是客户端/仓库的"类"，只用于类型标注，告诉读代码的人每个字段装的是什么东西
from app.client.custom_embedding_client import CustomEmbeddingClient  # 文本转向量模型的客户端
from app.repository.es.column_es_repository import ColumnEsRepository  # 用 ES 查字段里的具体取值
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository  # 用 MySQL 查字段信息
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository  # 用 MySQL 查表信息
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository  # 用 Qdrant 查字段向量
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository  # 用 Qdrant 查指标向量


# 运行时上下文的"字段清单"：每个节点通过 runtime.context["字段名"] 就能拿到对应客户端
class AgentRuntimeContext(TypedDict):
    embedding_client : CustomEmbeddingClient  # 把关键词变成向量，供向量库检索
    column_qdrant_repository: ColumnQdrantRepository  # 字段向量的检索入口
    metric_qdrant_repository: MetricQdrantRepository  # 指标向量的检索入口
    column_es_repository: ColumnEsRepository  # 具体取值的检索入口（ES 全文检索）
    # 空行只是排版，没有语法作用

    column_mysql_repository:ColumnInfoMySqlRepository  # 查字段详情、主外键等元数据
    table_mysql_repository: TableInfoMySqlRepository  # 查表名、表说明等元数据
    # 【注意】上下文里只有"元数据库"的连接，没有数仓（appConfig.db_dw）的连接。
    # 如果后续要在线执行生成的 SQL，需要再往这里加一个数仓客户端并由调用方注入。
