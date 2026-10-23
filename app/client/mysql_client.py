

from sqlalchemy.ext.asyncio import create_async_engine,sessionmaker


class CustomMysqlClient:
    def __init__(self, db_config):
        self.db_config = db_config
        self.engine = create_async_engine(
            f"mysql+aiomysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}",
            echo=True,
        )
        self.sessionLocal = sessionmaker(
            bind=self.engine, expire_on_commit=False
        )