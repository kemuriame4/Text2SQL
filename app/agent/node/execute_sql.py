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


async def executeSQL(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer
    generate_sql  = state['generate_sql']
    # 从上下文中获取数据仓库交互层对象dw_mysql_repository
    dw_mysql_repository = runtime.context['dw_mysql_repository']
    result = await  dw_mysql_repository.execute_sql(generate_sql)
    writer({'data':result})
    return {'result':result}




