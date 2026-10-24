from personal.config.app_config import LLMConfig
from langchain_google_genai import ChatGoogleGenerativeAI


class CustomLLMClient:
    def __init__(self, config: LLMConfig):
        self._config = config

    def get_client(self):
        self.client = ChatGoogleGenerativeAI(
            model_name=f"{self._config.generate.model}",
            google_api_key=f"{self._config.generate.api_key}",
        )
