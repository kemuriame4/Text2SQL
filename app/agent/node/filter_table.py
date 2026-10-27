import jieba.analyse
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.utils.loader_prompt_util import load_prompt_by_path


async def filterTable(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer
    writer('这是流式输出的第一个内容')
    table_infos = state["table_infos"]
    question  = state['question']

    # 使用大模型进行过滤
    prompt = PromptTemplate(
        template=load_prompt_by_path('filter_table_info'),
        input_variables=['query','table_infos'],
    )

    output = JsonOutputParser()
    chain = prompt | llm | output
    # allow_unicode 保留中文的Unicode 字符
    #sort_keys 是否保持原有的顺序
    result = await chain.ainvoke(
        {
            'query': question,
            'table_infos': yaml.dump(table_infos,allow_unicode=True,sort_keys=False),
        }
    )
    # 创建切片副本，避免遍历时修改原列表数据导致索引错误
    for table_info in table_infos[:]:
        if table_info['name'] not in result:
            table_infos.remove(table_info)
        else :
            selected_column = result[table_info['name']]

            for column_info in table_info['columns'][:]:
                if column_info['name'] not in selected_column:
                    table_info['columns'].remove(column_info)

    return {'table_infos':table_infos}