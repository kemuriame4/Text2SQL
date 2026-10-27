from datetime import datetime

import jieba.analyse
import yaml
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.utils.loader_prompt_util import load_prompt_by_path


async def generateSQL(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer
    metric_infos = state["metric_infos"]
    table_infos = state["table_infos"]
    question  = state['question']
    current_date = datetime.now().strftime('%Y-%m-%d')

    # 使用大模型进行过滤
    prompt = PromptTemplate(
        template=load_prompt_by_path('generate_sql'),
        input_variables=['query','metric_infos','table_infos','date_info'],
    )

    output = StrOutputParser()
    chain = prompt | llm | output
    # allow_unicode 保留中文的Unicode 字符
    #sort_keys 是否保持原有的顺序
    sql = await chain.ainvoke(
        {
            'query': question,
            'metric_infos': yaml.dump(metric_infos,allow_unicode=True,sort_keys=False),
            'table_infos': yaml.dump(table_infos,allow_unicode=True,sort_keys=False),
            'date_info': current_date,
        }
    )



    print('生成的sql语句为：',sql)

    return {'generate_sql':sql}