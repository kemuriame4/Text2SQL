from langchain_openai import OpenAIEmbeddings

from app.conf.app_config import EmbeddingConfig


class CustomEmbeddingClient:
    def __init__(self,config:EmbeddingConfig):
        self.config = config
        self._url = self._get_url()

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}/v1'

    def get_client(self):
        return OpenAIEmbeddings(
            base_url=self._url,
            api_key='unused',
            check_embedding_ctx_length=False,
        )