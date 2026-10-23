from qdrant_client import AsyncQdrantClient

from app.conf.app_config import QdrantConfig


class CustomQdrantClient:
    def __init__(self,config:QdrantConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        return f'http://{self._config.host}:{self._config.port}'

    def get_client(self):
        self.client = AsyncQdrantClient(url=self._url)