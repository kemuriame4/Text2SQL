import asyncio

from langgraph.constants import START
from langgraph.graph import StateGraph

from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.agent.node.column_call import retrievalColumns
from app.agent.node.keywords_ext import keywordsExt
from app.client.custom_embedding_client import CustomEmbeddingClient
from app.client.custom_qdrant_client import CustomQdrantClient
from app.conf.app_config import  appConfig
from app.repository.qdrant import column_qdrant_repository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository

graph = StateGraph(state_schema=AgentState,context_schema=AgentRuntimeContext)
# 添加节点
graph.add_node('keywords_ext',keywordsExt)
graph.add_node('retrievalColumns',retrievalColumns)
# 添加边
graph.add_edge('keywords_ext','retrievalColumns')
# 设置入口
graph.set_entry_point('keywords_ext')

# 编译
app = graph.compile()




async def test():
    # 执行
    init_state = {'question': '给我查询今年各地区第一季度的销售额'}
    # 实例化向量模型客户端
    embedding_client = CustomEmbeddingClient(appConfig.embedding).get_client()
    # 实例化ColumnQdrantRepository对象
    qdrant_client = CustomQdrantClient(appConfig.qdrant)
    qdrant_client.get_client()
    column_qdrant_repository = ColumnQdrantRepository(qdrant_client.client)

    # 将embedding客户和column_qdrant_repository存储到运行时上下文中
    context = AgentRuntimeContext(
        embedding_client=embedding_client,
        column_qdrant_repository=column_qdrant_repository
    )
    # 设置为流式输出
    # result = await  app.ainvoke(init_state)
    async  for chunk in app.astream(input=init_state,context=context,stream_mode='custom'):
        print(chunk)

if __name__ == '__main__':
    asyncio.run(test())