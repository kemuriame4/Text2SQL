import jieba.analyse
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.utils.loader_prompt_util import load_prompt_by_path


async def filterMetric(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer
    metric_infos = state["metric_infos"]
    question  = state['question']

    # 使用大模型进行过滤
    prompt = PromptTemplate(
        template=load_prompt_by_path('filter_metric_info'),
        input_variables=['query','metric_infos'],
    )

    output = JsonOutputParser()
    chain = prompt | llm | output
    # allow_unicode 保留中文的Unicode 字符
    #sort_keys 是否保持原有的顺序
    result = await chain.ainvoke(
        {
            'query': question,
            'metric_infos': yaml.dump(metric_infos,allow_unicode=True,sort_keys=False),
        }
    )
    # 创建切片副本，避免遍历时修改原列表数据导致索引错误
    for metric_info in metric_infos[:]:
        if metric_info['name'] not in result:
            metric_infos.remove(metric_info)


    print('过滤后的指标数据：',metric_infos)

    return {'metric_infos':metric_infos}