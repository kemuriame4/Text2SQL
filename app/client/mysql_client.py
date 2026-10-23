from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.engine import URL

from app.conf.app_config import DbConfig


class MysqlClient:
    """异步 MySQL 客户端：持有唯一的 async engine 和 session 工厂。"""

    def __init__(self, config: DbConfig):
        self._config = config
        self._url = self._get_url()
        self._engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker | None = None

    def _get_url(self) -> URL:
        # URL.create 会自动处理用户名/密码中的特殊字符转义
        return URL.create(
            drivername='mysql+asyncmy',
            username=self._config.username,
            password=self._config.password,
            host=self._config.host,
            port=self._config.port,
            database=self._config.database,
            query={'charset': 'utf8mb4'},
        )

    def get_session_factory(self) -> async_sessionmaker:
        """懒加载创建 engine（单例），返回 async_sessionmaker。"""
        if self._engine is None:
            self._engine = create_async_engine(
                self._url,
                pool_size=10,
                max_overflow=10,
                pool_timeout=30,      # 从连接池获取连接的等待上限（秒）
                pool_recycle=3600,    # 连接最长存活时间，避免 MySQL 8 小时断连
                pool_pre_ping=True,   # 取连接前探活，自动剔除失效连接
            )
            self.session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        return self.session_factory

    async def close(self) -> None:
        """释放连接池，进程退出或使用结束前必须调用。"""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self.session_factory = None
