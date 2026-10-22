from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DbConfig


class MysqlClient:
    def __init__(self, config: DbConfig):
        self._config = config
        self._url = self._get_url

    def _get_url(self):
        return f'mysql+pymysql://{self._config.username}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}'

    def get_session_factory(self):
        engine = create_async_engine(
            self._url,
            pool_size=10,
            max_overflow=10,
            pool_timeout=3600,
        )
        self.sessionFactory = async_sessionmaker(engine, expire_on_commit=False)
