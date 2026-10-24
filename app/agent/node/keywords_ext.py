import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState


async def keywordsExt(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer
    writer('这是流式输出的第一个内容')
    question = state["question"]

    # 使用jieba分词
    # uv add jieba
    # 根据自己定义的词性进行分词
    allow_pos =(
        "n",# 名称
        "nr", # 人名
        "ns", # 地点
        "nt",# 机构团体  学校  x公司
        "nz",# 其他的专业名词  哈希算法  Unicode
        "v",# 动词
        "vn",# 名动词
        "a",# 形容词
        "an",#  名形词
        "eng",#  英文
        "i",#  成语
        "l",#  常用固定短语
    )
    # 使用jieba的算法进行关键词的提取
    keywords = jieba.analyse.extract_tags(question, allowPOS=allow_pos)

    # 将原始的查询加入到关键词列表中
    keywords = list(set(keywords + [question]))
    writer(keywords)
    return {'keywords':keywords}