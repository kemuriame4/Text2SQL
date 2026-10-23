from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig


class CustomMySqlClient:
    def __init__(self,config:DBConfig):
        self._config = config
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()

    def _get_url(self):
        return f"mysql+asyncmy://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}"

    def get_session_factory(self):
        '''
        创建（并缓存）异步会话工厂
        【原写法的问题】每次调用都新建 engine，既不返回工厂也容易把连接池撑爆。
        '''
        if getattr(self, '_sessionFactory', None) is None:
            async_engine = create_async_engine(
                self._url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                # 连不上时快速失败，而不是一直挂着
                pool_pre_ping=True,
            )
            self._sessionFactory = async_sessionmaker(
                async_engine,
                expire_on_commit=False,
            )
        # 保留原来的属性名，老代码 self.sessionFactory() 也能用
        self.sessionFactory = self._sessionFactory
        return self._sessionFactory

