# 【文件作用】
# 这是图里的第 4 个节点（工位），负责"取值召回"：找出问题里提到的具体值（比如"华东""在职"）出现在哪些字段里。
# 它是三路并行检索（三件事同时干，不用排队）中的第三路，用的是 ES 全文检索（在文本里找包含关键词的内容）。
# 它从 state 里读 question 和 keywords，处理完返回 {'retrieval_values': [...]} 交给 merge_retrieved 节点。
from langchain_core.output_parsers import JsonOutputParser  # 导入 JSON 解析器（把大模型返回的文本解析成列表/字典）
from langchain_core.prompts import PromptTemplate  # 导入提示词模板（可以往模板里填空位）
from langgraph.runtime import Runtime  # 导入 Runtime 类型，只用来标注参数类型

from app.agent.agent_llm import llm  # 导入已经初始化好的大模型对象
from app.agent.agent_runtime_context import AgentRuntimeContext  # 导入运行时上下文的类型
from app.agent.agent_state import AgentState  # 导入全局状态的类型
from app.entity.value_info import ValueInfo  # 导入"字段取值"实体类（只用于类型标注）
from app.utils.loader_prompt_util import load_prompt_by_path  # 导入按文件名读取提示词文件的工具函数


# 【作用】定义"取值召回"节点函数。
# 处理流程：取问题和关键词 → 让大模型扩词 → 逐个关键词去 ES 全文索引搜字段取值。
async  def retrievalValue(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    # 【函数说明】这个节点分三件事：从状态中取出问题、关键词；扩词；召回（把相关取值搜出来）。
    '''
        从状态中取出问题、关键词
        扩词
        召回
    '''
    question = state["question"]  # 取出用户原始问题
    keywords = state["keywords"]  # 取出上一个节点切好的关键词列表

    # 从运行时上下文中获取对象
    column_es_repository = runtime.context['column_es_repository']  # 取出"字段取值全文索引"的查询对象
    # 使用大模型进行扩词

    prompt = PromptTemplate(  # 创建一个提示词模板对象
        template=load_prompt_by_path('extend_keywords_for_value_recall'),  # 读取 prompts 目录下对应的扩词提示词文本
        input_variables=['query']  # 声明模板里有一个叫 query 的空位，待会儿填用户问题
    )

    output = JsonOutputParser()  # 创建 JSON 解析器（把大模型返回的文本解析成 Python 列表）
    chain = prompt  | llm | output  # 竖线 | 表示串成流水线：先填模板 → 再交给大模型 → 最后解析成 JSON
    extended_keyworks = await chain.ainvoke({'query':question})  # 异步跑完整条流水线，拿到大模型给的扩展关键词列表
    # 【注意】变量名 keyworks 少写了一个 o，是拼写笔误，不影响运行。


    # 将扩展的提示词合并原来的keywords
    all_keywords = list(set(keywords + extended_keyworks))  # 原有词 + 扩展词拼一起，set 去重（同一个词只留一份）
    # 关键词检索内容
    retrieval_value_map : dict[str, ValueInfo]  = {}  # 空字典当"结果收纳盒"：键是取值 id，值是取值对象，顺便去重
    for keyword in all_keywords:  # 把每个关键词依次拿出来检索
        # 关键词检索
        values: list[ValueInfo] = await column_es_repository.search(keyword)  # 拿关键词去 ES 搜包含它的字段取值，最多回 5 条
        # 去重存储
        for value in values:  # 遍历搜回来的每一个取值
            value_id = value.id  # 取出取值的 id，当作去重的"钥匙"
            if value_id not in retrieval_value_map:  # 如果收纳盒里还没有这个 id
                retrieval_value_map[value_id] = value  # 就放进去；已经有就跳过（同一个取值只留一份）
        #将字段转换为列表
        retrieval_values = list(retrieval_value_map.values())  # 把字典里所有值（取值对象）取出来转成列表
        writer = runtime.stream_writer  # 拿到流式输出的写入口
        # 【注意】这里推给前端的是关键词列表，不是查到的取值，看起来更像调试输出，可以留意。
        writer(all_keywords)  # 把本轮使用的关键词推给前端
        writer(retrieval_values)  # 把当前已召回的取值实时推给前端
        # 【注意】下面这行 return 缩进在 for 循环内部：只处理完第一个关键词就返回了，其余关键词都被跳过，形同没循环。
        # 【注意】如果 all_keywords 是空列表，这个 return 根本不会执行，函数会返回 None，LangGraph 可能因此报错。
        return {'retrieval_values':retrieval_values, }  # 只返回本节点负责的取值列表，交给后面的合并节点



