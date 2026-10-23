
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig


class CustomMysqlClient:
    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        self.engine = create_async_engine(
            f"mysql+asyncmy://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}",
            echo=True,
        )
        # 异步会话工厂，必须用 async_sessionmaker，sessionmaker 不支持 async with
        self.sessionLocal = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )
