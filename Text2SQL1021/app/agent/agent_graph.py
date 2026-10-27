# 【文件作用】
# 这个文件是在线问答的入口，负责把 5 个节点装配成一张流程图并编译运行。
# 运行本文件会走 __main__ 里的测试代码：真正连上向量库/ES/MySQL，跑一遍完整链路。
# asyncio（Python 自带的"异步调度器"）：让多个"等网络"的任务交替执行，不用一个一个干等
import asyncio

# START（LangGraph 内置常量，代表图的"起点"）；不过本文件后面用的是 set_entry_point，所以它其实没被用到
from langgraph.constants import START
# StateGraph（一张流程图模板：节点是工位，边是"下一步去哪"的箭头）
from langgraph.graph import StateGraph

# AgentRuntimeContext（运行时上下文：节点要用的数据库/向量库客户端，运行前统一塞进这里）
from app.agent.agent_runtime_context import AgentRuntimeContext
# AgentState（图里流动的数据格式，规定这张图上有哪些字段）
from app.agent.agent_state import AgentState
# 下面 5 个 import 就是 5 个节点函数（每个节点 = 一个 async 函数，接收 state 和 runtime 两个参数）
from app.agent.node.column_call import retrievalColumns  # 节点：按关键词召回"字段"
from app.agent.node.keywords_ext import keywordsExt  # 节点：用 jieba 从问题里切关键词
from app.agent.node.merge_retrieved import mergeRetrieval  # 节点：把三路召回结果合并补全
from app.agent.node.metric_call import retrievalMetric  # 节点：按关键词召回"指标"
from app.agent.node.value_call import retrievalValue  # 节点：按关键词召回"具体取值"
# 各种客户端封装类：向量模型、Elasticsearch（全文检索引擎）、Qdrant（向量数据库）、MySQL
from app.client.custom_embedding_client import CustomEmbeddingClient
from app.client.custom_es_client import CustomESClient
from app.client.custom_qdrant_client import CustomQdrantClient
from app.client.mysql_client import CustomMySqlClient
# appConfig（全局配置对象，里面装的是从 yaml 配置文件里读出来的地址、账号、模型名等）
from app.conf.app_config import  appConfig
# 下面这些是"仓库类"（Repository）：把"怎么查库"包成一个个方法，节点里只管调用，不关心底层细节
from app.repository.es.column_es_repository import ColumnEsRepository
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.repository.qdrant import column_qdrant_repository, metric_qdrant_repository
# 【注意】上面这行导入的两个"模块"在后面并没有被使用（真正用的是下面两行导入的类），属于多余导入
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository

# 建图第一步：造一个空的流程图对象。
# state_schema 说明"图上流动的数据长什么样"；context_schema 说明"节点运行时能拿到哪些外部资源"。
graph = StateGraph(state_schema=AgentState,context_schema=AgentRuntimeContext)
# 添加节点
# add_node(名字, 函数)：把函数挂到图上的某个"工位"，这个名字后面连边时要用
graph.add_node('keywords_ext',keywordsExt)  # 第 1 站：jieba 分词，产出 keywords
graph.add_node('retrievalColumns',retrievalColumns)  # 第 2 站之一：召回字段
graph.add_node('retrievalMetric',retrievalMetric)  # 第 2 站之二：召回指标
graph.add_node('retrievalValue',retrievalValue)  # 第 2 站之三：召回取值
graph.add_node('mergeRetrieval',mergeRetrieval)  # 第 3 站：合并三路结果，补齐表/指标结构
# 添加边
# 并行处理
# add_edge(A, B)：画一条"A 干完就去 B"的箭头。
# 同一个节点引出 3 条箭头，就表示这 3 个下游节点会并行（同时）被触发。
graph.add_edge('keywords_ext','retrievalColumns')  # 分词完 → 召回字段
graph.add_edge('keywords_ext','retrievalMetric')  # 分词完 → 召回指标
graph.add_edge('keywords_ext','retrievalValue')  # 分词完 → 召回取值

# 合并处理
# 三路并行跑完后，都要汇到 mergeRetrieval；LangGraph 会等这几路都到齐再执行它
graph.add_edge('retrievalColumns','mergeRetrieval')  # 字段召回完 → 合并
graph.add_edge('retrievalMetric','mergeRetrieval')  # 指标召回完 → 合并
graph.add_edge('retrievalValue','mergeRetrieval')  # 取值召回完 → 合并

# 设置入口
# set_entry_point(名字)：用户一调用，就从图上这个节点开始跑
graph.set_entry_point('keywords_ext')

# 编译
# 编译 compile（把画好的图变成真正能跑的对象）；之后用 app.astream / app.ainvoke 触发执行
app = graph.compile()




# 测试函数：手动把各种客户端连好，然后跑一次完整问答，用来验证整条链路通不通
# async def 表示这是"异步函数"（里面用 await 等网络返回时，程序可以先去干别的）
async def test():
    # 执行
    # init_state（初始状态）：图一开始拿到的数据，只需要一个用户问题；其它字段由节点跑出来后再补进去
    init_state = {'question': '给我查询今年各地区第一季度的销售额'}
    # 实例化向量模型客户端
    # configs.embedding 里的 host/port 指向一个"文本转向量"的服务；get_client() 返回可调用的客户端对象
    embedding_client = CustomEmbeddingClient(appConfig.embedding).get_client()
    # 实例化ColumnQdrantRepository对象
    qdrant_client = CustomQdrantClient(appConfig.qdrant)  # 先造一个"连接管理器"，此时还没连
    qdrant_client.get_client()  # 真正建连：内部把连接对象存到自己的 client 属性上
    # 用同一个连接分别造"字段仓库"和"指标仓库"，两者查的是 Qdrant 里不同的集合
    column_qdrant_repository = ColumnQdrantRepository(qdrant_client.client)
    metric_qdrant_repository = MetricQdrantRepository(qdrant_client.client)

    # 实例化es的客户端
    # es（Elasticsearch）：这里用来按关键词精确检索字段里出现过的"具体值"
    es_client = CustomESClient(appConfig.es).get_client()
    column_es_repository = ColumnEsRepository(es_client)  # 把 ES 连接包成"字段取值仓库"

    # 实例mysql客户端
    # 元数据库（db_meta）：存的是"数仓的表结构/字段/指标"这类元信息
    meta_mysql_client = CustomMySqlClient(appConfig.db_meta)
    meta_mysql_client.get_session_factory()  # 建连接池 + 会话工厂，同样是存在对象属性里
    sessionFactory = meta_mysql_client.sessionFactory  # 把会话工厂取出来，下面要用它开数据库会话
    # async with 是异步版的 with：进入时打开会话，代码块结束后自动关闭（即使中途报错也会关）
    async  with sessionFactory() as meta_session:
        # 两个 MySQL 仓库共用同一个会话，分别负责查"字段信息"和"表信息"
        column_mysql_repository = ColumnInfoMySqlRepository(meta_session)
        table_mysql_repository = TableInfoMySqlRepository(meta_session)

        # 将embedding客户和column_qdrant_repository存储到运行时上下文中
        # context（运行时上下文）只放"外部连接资源"这些不变的东西，节点执行时通过 runtime.context[...] 取用
        context = AgentRuntimeContext(
            embedding_client=embedding_client,  # 文本转向量
            column_qdrant_repository=column_qdrant_repository,  # 查字段向量库
            metric_qdrant_repository=metric_qdrant_repository,  # 查指标向量库
            column_es_repository=column_es_repository,  # 查字段取值（ES）
            column_mysql_repository=column_mysql_repository,  # 查字段/主外键（MySQL）
            table_mysql_repository=table_mysql_repository,  # 查表结构（MySQL）
        )
        # 设置为流式输出
        # result = await  app.ainvoke(init_state)
        # 【注意】上面这行被注释掉了：ainvoke 是"等全部算完一次性返回"，而且这里没传 context。
        # 若想改回非流式，应写成 app.ainvoke(init_state, context=context)。
        # 流式输出（一边算一边往外吐结果，不用等全部算完）：astream 返回一个可以 for 循环的"异步迭代器"
        # stream_mode='custom' 表示只接收节点里用 runtime.stream_writer(...) 主动写出的内容
        async  for chunk in app.astream(input=init_state,context=context,stream_mode='custom'):
            print(chunk)  # 每收到一段就打印出来，方便观察每个节点跑到了哪一步

# 只有"直接 python 运行本文件"时，下面的代码才会执行；被别的文件 import 时不会跑（避免误触发测试）
if __name__ == '__main__':
    asyncio.run(test())  # 启动异步事件循环，把 test() 这个异步函数跑起来
