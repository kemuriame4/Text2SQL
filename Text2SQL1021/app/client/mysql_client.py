# 【文件作用】
# 这个文件是"接线员"，负责创建并维持和 MySQL 的连接。
# 用的是 SQLAlchemy 的异步引擎 async engine（发请求后不用干等，可以同时干别的），底层驱动选 asyncmy。
# 连接参数来自 conf/app_config.yaml，经 app/conf/app_config.py 读取后全局可用（appConfig.db_meta / appConfig.db_dw）。

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # create_async_engine：造异步引擎；async_sessionmaker：造"会话工厂"（批量生产会话）

from app.conf.app_config import DBConfig  # 数据库配置的模板类（规定要有 host / port / user / password / database）


class CustomMySqlClient:  # 定义"MySQL 连接管理器"类：一个对象管一套连接
    def __init__(self,config:DBConfig):  # 构造方法：创建对象时传进一块数据库配置
        self._config = config  # 把配置存成私有属性（下划线开头 = 约定只在类内部用）
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()  # 调下面的方法拼出连接串，先存起来备用

    def _get_url(self):  # 内部方法：拼数据库连接串
        # 【作用】拼出形如 mysql+asyncmy://用户:密码@主机:端口/库名 的连接串
        # mysql+asyncmy = MySQL 方言 + asyncmy 异步驱动；各段之间用 : 和 @ 分隔
        # 【注意】密码是明文拼进 URL 的，别把连接串打印到日志里
        return f"mysql+asyncmy://{self._config.user}:{self._config.password}@{self._config.host}:{self._config.port}/{self._config.database}"

    def get_session_factory(self):  # 建连接池（提前准备好几条连接，反复用，省得每次新建）+ 会话工厂
        async_engine = create_async_engine(  # 创建异步引擎（内部管着一个连接池，是连接的总管）
            self._url,  # 上面拼好的连接串
            pool_size=10,  # 连接池里常备 10 条连接
            max_overflow=20,  # 忙不过来时最多再临时多开 20 条（用完还回去）
            pool_recycle=3600  # 一条连接活满 3600 秒就重建，防止被 MySQL 主动断开后还拿来用
        )
        # 创建会话工厂
        self.sessionFactory = async_sessionmaker(  # 生成"会话工厂"：每次调用它（sessionFactory()）产出一个会话
            async_engine,  # 交给它上面造好的引擎
            expire_on_commit=False,  # 提交后不让对象"过期"（否则提交后再读对象属性还得回库重查一次）
        )
        # 【注意】本方法没有写 return，结果是挂在对象的 sessionFactory 属性上；
        # 调用方必须先调它，再取 client.sessionFactory 才能拿到工厂（本项目就是这么用的）
