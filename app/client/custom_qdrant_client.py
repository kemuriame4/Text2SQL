from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig, QdrantConfig


class CustomQdrantClient:
    def __init__(self,config:QdrantConfig):
        self._config = config
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()

    def _get_url(self):
        return f"http://{self._config.host}:{self._config.port}"

    def get_client(self):
        self.client = AsyncQdrantClient(url=self._url)

