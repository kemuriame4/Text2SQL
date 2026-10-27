# 【文件作用】
# 这个文件是"接线员"，负责创建并维持和 Qdrant 向量库的连接。
# 向量库（专门存向量、按"意思相近"做相似度检索的数据库）；本项目用它存字段和指标的文本向量。
# 连接参数来自 conf/app_config.yaml 的 qdrant 段，经 app/conf/app_config.py 读取后全局可用（appConfig.qdrant）。

from qdrant_client import AsyncQdrantClient  # 异步 Qdrant 客户端（发请求不用干等）
# 【注意】下面这一行是 SQLAlchemy 的引擎/会话工厂，本文件根本没用，是从 mysql_client.py 复制来的残留
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig, QdrantConfig  # 【注意】只用到 QdrantConfig；DBConfig 没用到，也是复制残留


class CustomQdrantClient:  # 定义"Qdrant 连接管理器"类
    def __init__(self,config:QdrantConfig):  # 构造方法：传入向量库配置（只需要 host + port）
        self._config = config  # 存下配置
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()  # 调下面的方法拼出服务地址，先存起来

    def _get_url(self):  # 内部方法：拼向量库的服务地址
        # 【作用】拼出形如 http://主机:端口 的地址（Qdrant 默认走 HTTP 协议）
        return f"http://{self._config.host}:{self._config.port}"

    def get_client(self):  # 真正建立（创建）客户端
        # 【注意】这里没有 return，客户端被挂到了对象的 client 属性上；
        # 调用方如果写 CustomQdrantClient(...).get_client()，拿到的是 None；
        # 正确用法是先调 get_client()，再从对象的 client 属性取（本项目就是 custom.client 这样取的）
        self.client = AsyncQdrantClient(url=self._url)  # 创建异步客户端，赋给自己的 client 属性
