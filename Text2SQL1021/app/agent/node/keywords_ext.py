# 【文件作用】
# 这是图里的第 1 个节点（工位），也是整条链路的入口，负责把用户的中文问题切成关键词。
# 它从 state 里读 question，处理完返回 {'keywords': [...]}，后面三路检索节点会同时用到它。
import jieba.analyse  # 导入 jieba 分词库里的 analyse 模块（专门用来做关键词提取）
from langgraph.runtime import Runtime  # 导入 Runtime 类型，只用来标注第二个参数的类型

from app.agent.agent_runtime_context import AgentRuntimeContext  # 导入"运行时上下文"类型（里面装着数据库、向量库等共享客户端）
from app.agent.agent_state import AgentState  # 导入"全局状态"类型（节点之间传数据用的大字典）


# 【作用】定义"关键词提取"节点函数。
# state 是全局状态字典，runtime 是运行时环境（能拿共享客户端，也能实时往前端推消息）。
async def keywordsExt(state:AgentState,runtime: Runtime[AgentRuntimeContext]):

    writer = runtime.stream_writer  # 拿到"流式输出"的写入口，调用它就能实时推一条消息给前端
    # 【注意】这里每次都推同一句固定文案，像是调试留下的，正式环境一般会去掉。
    writer('这是流式输出的第一个内容')
    question = state["question"]  # 从全局状态里取出用户最初问的那句中文问题

    # 使用jieba分词
    # uv add jieba
    # 根据自己定义的词性进行分词
    # 【补充】allow_pos 是"允许保留的词性"清单：jieba 会给每个词打词性标签，
    # 只有标签在这个元组（用逗号隔开、整体不可修改的一组值）里的词，才会被当作关键词。
    # 下面每一行末尾原有的注释，就是各个词性代号的中文含义。
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
    keywords = jieba.analyse.extract_tags(question, allowPOS=allow_pos)  # 真正执行提取，返回一个关键词列表（默认按重要程度排序）

    # 将原始的查询加入到关键词列表中
    keywords = list(set(keywords + [question]))  # 把原问题也拼进去，set 用来去重（同一个词只留一份），再转回列表
    # 【注意】set 是"无序集合"，转回列表后顺序是随机的，每次运行可能不一样。
    writer(keywords)  # 把这批关键词实时推给前端看
    return {'keywords':keywords}  # 只返回本节点负责的那部分状态，LangGraph 会自动合并进全局 state