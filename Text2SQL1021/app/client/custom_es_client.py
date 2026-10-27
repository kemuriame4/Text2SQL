# 【文件作用】
# 这个文件是"接线员"，负责创建并维持和 Elasticsearch（ES，专门做全文检索/关键词搜索的引擎）的连接。
# 本项目用 ES 按关键词精确检索字段里出现过的"具体值"（比如地区名、产品名）。
# 连接参数来自 conf/app_config.yaml 的 es 段，经 app/conf/app_config.py 读取后全局可用（appConfig.es）。

from elasticsearch import AsyncElasticsearch  # 异步 ES 客户端（本文件唯一真正用得上的 import）
from langchain_openai import OpenAIEmbeddings  # 【注意】没用的 import：OpenAIEmbeddings 本文件完全没用到，是从 embedding 客户端复制来的残留
from qdrant_client import AsyncQdrantClient  # 【注意】没用的 import：AsyncQdrantClient 本文件也没用到

from app.conf.app_config import QdrantConfig, EmbeddingConfig, ESConfig  # 【注意】只用到 ESConfig；QdrantConfig、EmbeddingConfig 都是复制残留


class CustomESClient:  # 定义"ES 连接管理器"类
    def __init__(self,config:ESConfig):  # 构造方法：传入 ES 配置（只需要 host + port）
        self._config = config  # 存下配置
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()  # 调下面的方法拼出服务地址


    def _get_url(self):  # 内部方法：拼 ES 的服务地址
        # 【作用】拼出形如 http://主机:端口 的地址
        return f"http://{self._config.host}:{self._config.port}"

    def get_client(self):  # 创建并返回 ES 客户端
        # 【注意】每调用一次就新建一个客户端（ES 官方建议整个程序共用一个），
        # 旧的不 close() 会一直占着连接；本项目里一般只建一次，问题不大
        return AsyncElasticsearch([self._url])  # 传地址列表（ES 支持多个节点，这里只有一个）
