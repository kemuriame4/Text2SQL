from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import create_async_engine,sessionmaker

from app.conf.app_config import QdrantConfig


class CustomQdrantClient:
    def __init__(self, config:QdrantConfig):
        self._config = config
        self.url = self.getUrl()
        self.get_client()

    def getUrl(self):
        return f"http://{self._config.host}:{self._config.port}"
    
    def get_client(self):
        self.client = AsyncQdrantClient(url=self._url)
