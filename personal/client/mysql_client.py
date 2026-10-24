from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from personal.config.app_config import DatabaseConfig


class CustomMysqlClient:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._url = self._get_url()

    def _get_url(self):
        # 构造数据库连接URL
        database_login = f"{self._config.username}:{self._config.password}"
        database_address = f"{self._config.host}:{self._config.port}"
        database_name = f"{self._config.database}"
        return f"mysql+asyncmy://{database_login}@{database_address}/{database_name}"

    def get_session_factory(self):
        # 创建异步数据库引擎
        async_engine = create_async_engine(
            self._url, pool_size=10, max_overflow=20, pool_recycle=3600
        )
        # 创建会话工厂
        self.sessionFactory = async_sessionmaker(
            async_engine,
            expire_on_commit=False,
        )
