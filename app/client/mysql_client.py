"""MySQL 异步客户端：按 DBConfig 拼连接串，创建异步引擎和会话工厂。"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig


class CustomMySqlClient:
    """一个库对应一个实例：元数据库和数据仓库各建一个。"""
    def __init__(self,config:DBConfig):
        """
        做什么：保存配置，并在构造时就算好数据库连接串。
        参数：
        config (DBConfig)：一个库的连接配置（host / port / user / password / database）。
        返回：
        无（构造函数）。实例创建后即可调用 get_session_factory()。
        """
        self._config = config
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()

    def _get_url(self):
        """
        做什么：把配置拼成 SQLAlchemy 的异步连接串。
        参数：
        无，读取 self._config。
        返回：
        str：形如 mysql+asyncmy://user:password@host:port/database。
        注意：密码里的 @ : / 等特殊字符没有做转义，密码含这些字符时连接会失败。
        """
        return f"mysql+asyncmy://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}"

    def get_session_factory(self):
        """
        做什么：创建异步引擎和会话工厂，把会话工厂挂到 self.sessionFactory 上。
        参数：
        无。
        返回：
        None。会话工厂不是通过返回值拿，而是用 self.sessionFactory 访问。
        注意：① 没有返回值，写成 factory = client.get_session_factory() 会得到 None；
             ② 方法名是 get 开头，但实际是"设置"，每调用一次就新建一个引擎和连接池，
                旧引擎不会被关闭，重复调用会累积连接。
        """
        async_engine = create_async_engine(
            self._url,
            pool_size=10,          # 常驻连接数
            max_overflow=20,       # 峰值可临时多开 20 个
            pool_recycle=3600      # 连接超过 1 小时就回收重建
        )
        # 创建会话工厂
        self.sessionFactory = async_sessionmaker(
            async_engine,
            expire_on_commit=False,  # 提交后对象仍可读，不会被标成过期
        )

