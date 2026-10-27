from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState
from app.client.custom_embedding_client import CustomEmbeddingClient
from app.entity.column_info_entity import ColumnInfoEntity
from app.utils.loader_prompt_util import load_prompt_by_path


async  def retrievalColumns(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    '''
        从状态中取出问题、关键词
        扩词
        召回
    '''
    question = state["question"]
    keywords = state["keywords"]

    # 从运行时上下文中获取对象
    embedding_client  = runtime.context["embedding_client"]
    column_qdrant_repository = runtime.context["column_qdrant_repository"]

    # 使用大模型进行扩词

    prompt = PromptTemplate(
        template=load_prompt_by_path('extend_keywords_for_column_recall'),
        input_variables=['query']
    )

    output = JsonOutputParser()
    chain = prompt  | llm | output
    extended_keyworks = await chain.ainvoke({'query':question})
    # 将扩展的提示词合并原来的keywords
    all_keywords = list(set(keywords + extended_keyworks))
    # 向量数据库检索内容
    retrieval_columns_map : dict[str, ColumnInfoEntity]  = {}
    for keyword in all_keywords:
        # 向量化keyword
        embeddings = await embedding_client.aembed_query(keyword)
        # 检索
        payloads: list[ColumnInfoEntity] = await column_qdrant_repository.search(embeddings)
        # 去重存储
        for payload in payloads:
            column_id = payload.id
            if column_id not in retrieval_columns_map:
                retrieval_columns_map[column_id] = payload
        #将字段转换为列表
        retrieval_columns = list(retrieval_columns_map.values())
        writer = runtime.stream_writer
        writer(retrieval_columns)
        return {'retrieval_columns':retrieval_columns,}



