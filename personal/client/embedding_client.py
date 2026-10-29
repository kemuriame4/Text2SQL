from langchain_openai import OpenAIEmbeddings
from personal.config.app_config import EmbeddingConfig


class CustomEmbeddingClient:
    def __init__(self, config: EmbeddingConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        embedding_address = f"{self._config.host}:{self._config.port}"
        return f"http://{embedding_address}/v1"

    def get_client(self):
        self.client = OpenAIEmbeddings(
            base_url=self._url,
            api_key="unused",  # TEI does not require authentication by default
            check_embedding_ctx_length=False,
        )
        return self.client

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        if not hasattr(self, "client") or self.client is None:
            self.get_client()
        return await self.client.aembed_documents(texts)
