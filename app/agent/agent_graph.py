import asyncio

from langgraph.constants import START
from langgraph.graph import StateGraph

from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.agent.node.column_call import retrievalColumns
from app.agent.node.execute_sql import executeSQL
from app.agent.node.filter_metric import filterMetric
from app.agent.node.filter_table import filterTable
from app.agent.node.generate_sql import generateSQL
from app.agent.node.keywords_ext import keywordsExt
from app.agent.node.merge_retrieved import mergeRetrieval
from app.agent.node.metric_call import retrievalMetric
from app.agent.node.value_call import retrievalValue
from app.client.custom_embedding_client import CustomEmbeddingClient
from app.client.custom_es_client import CustomESClient
from app.client.custom_qdrant_client import CustomQdrantClient
from app.client.mysql_client import CustomMySqlClient
from app.conf.app_config import  appConfig
from app.repository.es.column_es_repository import ColumnEsRepository
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.dw.dw_mysql_repostory import DwMysqlRepostory
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.repository.qdrant import column_qdrant_repository, metric_qdrant_repository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository

graph = StateGraph(state_schema=AgentState,context_schema=AgentRuntimeContext)
# 添加节点
graph.add_node('keywords_ext',keywordsExt)
graph.add_node('retrievalColumns',retrievalColumns)
graph.add_node('retrievalMetric',retrievalMetric)
graph.add_node('retrievalValue',retrievalValue)
graph.add_node('mergeRetrieval',mergeRetrieval)
graph.add_node('filterTable',filterTable)
graph.add_node('filterMetric',filterMetric)
graph.add_node('generateSQL',generateSQL)
graph.add_node('executeSQL',executeSQL)
# 添加边
# 并行处理
graph.add_edge('keywords_ext','retrievalColumns')
graph.add_edge('keywords_ext','retrievalMetric')
graph.add_edge('keywords_ext','retrievalValue')

# 合并处理
graph.add_edge('retrievalColumns','mergeRetrieval')
graph.add_edge('retrievalMetric','mergeRetrieval')
graph.add_edge('retrievalValue','mergeRetrieval')

graph.add_edge('mergeRetrieval','filterTable')
graph.add_edge('mergeRetrieval','filterMetric')

graph.add_edge('filterMetric','generateSQL')
graph.add_edge('filterTable','generateSQL')
graph.add_edge('generateSQL','executeSQL')


# 设置入口
graph.set_entry_point('keywords_ext')

# 编译
app = graph.compile()
async def test():
    # 执行
    init_state = {'question': '给我查询去年各地区第一季度的销售额'}
    # 实例化向量模型客户端
    embedding_client = CustomEmbeddingClient(appConfig.embedding).get_client()
    # 实例化ColumnQdrantRepository对象
    qdrant_client = CustomQdrantClient(appConfig.qdrant)
    qdrant_client.get_client()
    column_qdrant_repository = ColumnQdrantRepository(qdrant_client.client)
    metric_qdrant_repository = MetricQdrantRepository(qdrant_client.client)

    # 实例化es的客户端
    es_client = CustomESClient(appConfig.es).get_client()
    column_es_repository = ColumnEsRepository(es_client)

    # 实例mysql客户端
    meta_mysql_client = CustomMySqlClient(appConfig.db_meta)
    meta_mysql_client.get_session_factory()
    sessionFactory = meta_mysql_client.sessionFactory

    # 初始化数据仓库连接对象
    dw_mysql_client = CustomMySqlClient(appConfig.db_dw)
    #  创建会话工厂
    dw_mysql_client.get_session_factory()
    # 获取会话工厂对象
    dw_session_factory = dw_mysql_client.sessionFactory

    async  with (sessionFactory() as meta_session,dw_session_factory() as dw_session):
        column_mysql_repository = ColumnInfoMySqlRepository(meta_session)
        table_mysql_repository = TableInfoMySqlRepository(meta_session)

        dw_mysql_repository = DwMysqlRepostory(dw_session)

        # 将embedding客户和column_qdrant_repository存储到运行时上下文中
        context = AgentRuntimeContext(
            embedding_client=embedding_client,
            column_qdrant_repository=column_qdrant_repository,
            metric_qdrant_repository=metric_qdrant_repository,
            column_es_repository=column_es_repository,
            column_mysql_repository=column_mysql_repository,
            table_mysql_repository=table_mysql_repository,
            dw_mysql_repository = dw_mysql_repository,
        )
        # 设置为流式输出
        # result = await  app.ainvoke(init_state)
        async  for chunk in app.astream(input=init_state,context=context,stream_mode='custom'):
            print(chunk)

if __name__ == '__main__':
    asyncio.run(test())