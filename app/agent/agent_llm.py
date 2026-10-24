from langchain_openai import ChatOpenAI

from app.conf.app_config import LLMConfig, appConfig


def initLLM(config: LLMConfig):
    return  ChatOpenAI(
        base_url= config.base_url,
        api_key= config.api_key,
        model= config.model,
    )

llm = initLLM(appConfig.llm)
