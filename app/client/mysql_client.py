from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig


class CustomMysqlClient:
    def __init__(self,config:DBConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        return f"mysql+asyncmy://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}"

    def get_session_factory(self):
        async_engine = create_async_engine(
            self._url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
        # 创建会话工厂
        self.session_factory = async_sessionmaker(
            async_engine,
            expire_on_commit=False,
        )