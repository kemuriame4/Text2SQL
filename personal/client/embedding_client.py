from qdrant_client import AsyncQdrantClient
from app.conf.app_config import EmbeddingConfig


class CustomEmbeddingClient:
    def __init__(self, config: EmbeddingConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        embedding_address = f"{self._config.host}:{self._config.port}"

        return f"http://{embedding_address}/v1"

    def get_client(self):
        self.client = AsyncQdrantClient(url=self._url)
