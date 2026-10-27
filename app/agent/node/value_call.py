from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.entity.value_info import ValueInfo
from app.utils.loader_prompt_util import load_prompt_by_path


async  def retrievalValue(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    '''
        从状态中取出问题、关键词
        扩词
        召回
    '''
    question = state["question"]
    keywords = state["keywords"]

    # 从运行时上下文中获取对象
    column_es_repository = runtime.context['column_es_repository']
    # 使用大模型进行扩词

    prompt = PromptTemplate(
        template=load_prompt_by_path('extend_keywords_for_value_recall'),
        input_variables=['query']
    )

    output = JsonOutputParser()
    chain = prompt  | llm | output
    extended_keyworks = await chain.ainvoke({'query':question})


    # 将扩展的提示词合并原来的keywords
    all_keywords = list(set(keywords + extended_keyworks))
    # 关键词检索内容
    retrieval_value_map : dict[str, ValueInfo]  = {}
    for keyword in all_keywords:
        # 关键词检索
        values: list[ValueInfo] = await column_es_repository.search(keyword)
        # print('查询的关键字为',keyword)
        # print('查询的关键字结果为：',values)
        # 去重存储
        for value in values:
            value_id = value.id
            if value_id not in retrieval_value_map:
                retrieval_value_map[value_id] = value
    #将字段转换为列表
    retrieval_values = list(retrieval_value_map.values())
    # writer = runtime.stream_writer
    # writer(all_keywords)
    # writer(retrieval_values)
    print('取值召回数据：',retrieval_values)
    return {'retrieval_values':retrieval_values, }



