import asyncio

from langgraph.constants import START
from langgraph.graph import StateGraph

from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.agent.node.keywords_ext import keywordsExt

graph = StateGraph(state_schema=AgentState,context_schema=AgentRuntimeContext)
# 添加节点
graph.add_node('keywords_ext',keywordsExt)
# 添加边

# 设置入口
graph.set_entry_point('keywords_ext')

# 编译
app = graph.compile()




async def test():
    # 执行
    init_state = {'question': '给我查询今年各地区第一季度的销售额'}
    context = AgentRuntimeContext()
    # 设置为流式输出
    # result = await  app.ainvoke(init_state)
    async  for chunk in app.astream(input=init_state,context=context,stream_mode='custom'):
        print(chunk)

if __name__ == '__main__':
    asyncio.run(test())