# 【文件作用】
# 这是图里的第 3 个节点（工位），负责"指标召回"：找出回答这个问题要用到哪些业务指标（比如销售额、转化率）。
# 它是三路并行检索（三件事同时干，不用排队）中的第二路。
# 它从 state 里读 question 和 keywords，处理完返回 {'retrieval_metrics': [...]} 交给 merge_retrieved 节点。
from langchain_core.output_parsers import JsonOutputParser  # 导入 JSON 解析器（把大模型返回的文本解析成列表/字典）
from langchain_core.prompts import PromptTemplate  # 导入提示词模板（可以往模板里填空位）
from langchain_openai import OpenAIEmbeddings  # 【注意】导入了但本文件没用到（多余的 import）
from langgraph.runtime import Runtime  # 导入 Runtime 类型，只用来标注参数类型

from app.agent.agent_llm import llm  # 导入已经初始化好的大模型对象
from app.agent.agent_runtime_context import AgentRuntimeContext  # 导入运行时上下文的类型
from app.agent.agent_state import AgentState  # 导入全局状态的类型
from app.client.custom_embedding_client import CustomEmbeddingClient  # 【注意】导入了但本文件没用到
from app.entity.column_info_entity import ColumnInfoEntity  # 【注意】导入了但本文件没用到
from app.entity.metric_info_entity import MetricInfoEntity  # 导入"指标信息"实体类（只用于类型标注）
from app.repository.qdrant import metric_qdrant_repository  # 【注意】这里导入的模块级对象，在函数里又被运行时上下文中的同名变量覆盖了，实际没用到
from app.utils.loader_prompt_util import load_prompt_by_path  # 导入按文件名读取提示词文件的工具函数


# 【作用】定义"指标召回"节点函数。
# 处理流程：取问题和关键词 → 让大模型扩词 → 逐个关键词去 Qdrant 向量库搜相似指标。
async  def retrievalMetric(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    # 【函数说明】这个节点分三件事：从状态中取出问题、关键词；扩词；召回（把相关指标搜出来）。
    '''
        从状态中取出问题、关键词
        扩词
        召回
    '''
    question = state["question"]  # 取出用户原始问题
    keywords = state["keywords"]  # 取出上一个节点切好的关键词列表

    # 从运行时上下文中获取对象
    embedding_client  = runtime.context["embedding_client"]  # 取出"向量化客户端"（能把一段文字变成一串数字）
    metric_qdrant_repository = runtime.context["metric_qdrant_repository"]  # 取出"指标向量库"的查询对象
    # 使用大模型进行扩词

    prompt = PromptTemplate(  # 创建一个提示词模板对象
        template=load_prompt_by_path('extend_keywords_for_metric_recall'),  # 读取 prompts 目录下对应的扩词提示词文本
        input_variables=['query']  # 声明模板里有一个叫 query 的空位，待会儿填用户问题
    )

    output = JsonOutputParser()  # 创建 JSON 解析器（把大模型返回的文本解析成 Python 列表）
    chain = prompt  | llm | output  # 竖线 | 表示串成流水线：先填模板 → 再交给大模型 → 最后解析成 JSON
    extended_keyworks = await chain.ainvoke({'query':question})  # 异步跑完整条流水线，拿到大模型给的扩展关键词列表
    # 【注意】变量名 keyworks 少写了一个 o，是拼写笔误，不影响运行。
    # 将扩展的提示词合并原来的keywords
    all_keywords = list(set(keywords + extended_keyworks))  # 原有词 + 扩展词拼一起，set 去重（同一个词只留一份）
    # 向量数据库检索内容
    retrieval_metrics_map : dict[str, MetricInfoEntity]  = {}  # 空字典当"结果收纳盒"：键是指标 id，值是指标对象，顺便去重
    for keyword in all_keywords:  # 把每个关键词依次拿出来检索
        # 向量化keyword
        embeddings = await embedding_client.aembed_query(keyword)  # 向量化（把关键词变成一串数字，方便计算机比较"像不像"）
        # 检索
        payloads: list[MetricInfoEntity] = await metric_qdrant_repository.search(embeddings)  # 拿这串数字去向量库搜最相似的指标，最多回 5 个
        # 去重存储
        for payload in payloads:  # 遍历搜回来的每一个指标
            metric_id = payload.id  # 取出指标的 id，当作去重的"钥匙"
            if metric_id not in retrieval_metrics_map:  # 如果收纳盒里还没有这个 id
                retrieval_metrics_map[metric_id] = payload  # 就放进去；已经有就跳过（同一个指标只留一份）
        #将字段转换为列表
        retrieval_metrics = list(retrieval_metrics_map.values())  # 把字典里所有值（指标对象）取出来转成列表
        writer = runtime.stream_writer  # 拿到流式输出的写入口
        writer(retrieval_metrics)  # 把当前已召回的指标实时推给前端
        # 【注意】下面这行 return 缩进在 for 循环内部：只处理完第一个关键词就返回了，其余关键词都被跳过，形同没循环。
        # 【注意】如果 all_keywords 是空列表，这个 return 根本不会执行，函数会返回 None，LangGraph 可能因此报错。
        return {'retrieval_metrics':retrieval_metrics, }  # 只返回本节点负责的指标列表，交给后面的合并节点



