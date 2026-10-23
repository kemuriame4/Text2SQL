from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from APP.config.APP_config import DBConfig


class CustomMySqlClient:
    def __init__(self ,config:DBConfig):
        self._config = config
        self._url = self._get_url()

    def get_url(self):
        return f"mysql + asyncmy://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}"

    def get_session_factory(self):
        async_engine = create_async_engine(
            self._url ,
            pool_size = 10 ,
            max_overflow = 20 ,
            pool_recycle = 3600 ,
        )

        self.sessionFactory = async_sessionmaker(
            async_engine ,
            expire_on_commit = False ,
        )