from elasticsearch import AsyncElasticsearch
from app.conf.app_config import ESConfig


class CustomESClient:
    def __init__(self, config: ESConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        es_address = f"{self._config.host}:{self._config.port}"

        return f"http://{es_address}"

    def get_client(self):
        self.client = AsyncElasticsearch([self._url])
