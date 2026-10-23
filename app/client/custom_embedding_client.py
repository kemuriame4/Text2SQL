from langchain_openai import OpenAIEmbeddings
from qdrant_client import AsyncQdrantClient

from app.conf.app_config import QdrantConfig, EmbeddingConfig


class CustomEmbeddingClient:
    def __init__(self,config:EmbeddingConfig):
        self._config = config
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()


    def _get_url(self):
        return f"http://{self._config.host}:{self._config.port}/v1"

    def get_client(self):
        return OpenAIEmbeddings(
            base_url=self._url,
            api_key="unused",  # TEI does not require authentication by default
            check_embedding_ctx_length=False,
        )

