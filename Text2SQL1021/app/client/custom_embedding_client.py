# 【文件作用】
# 这个文件是"接线员"，负责创建并维持和"向量化服务"的连接。
# 向量化 / embedding（把一句话变成一串数字，方便比较意思像不像）；
# 本项目用 TEI（Text Embeddings Inference，自部署的向量化服务）把文本变成 1024 维向量。
# 连接参数来自 conf/app_config.yaml 的 embedding 段，经 app/conf/app_config.py 读取后全局可用（appConfig.embedding）。

from langchain_openai import OpenAIEmbeddings  # 用 OpenAI 兼容的客户端调 TEI（TEI 的接口和 OpenAI 的 /v1/embeddings 长得一样）
from qdrant_client import AsyncQdrantClient  # 【注意】没用的 import：本文件完全没用到，是复制残留

from app.conf.app_config import QdrantConfig, EmbeddingConfig  # 【注意】只用到 EmbeddingConfig；QdrantConfig 没用到，也是复制残留


class CustomEmbeddingClient:  # 定义"向量化服务连接管理器"类
    def __init__(self,config:EmbeddingConfig):  # 构造方法：传入配置（host / port / embedding_size）
        self._config = config  # 存下配置
        # 构造函数调用_get_url()获取数据的连接地址，结果赋值给_url
        self._url = self._get_url()  # 调下面的方法拼出服务地址


    def _get_url(self):  # 内部方法：拼向量化服务的地址
        # 【作用】末尾的 /v1 是 OpenAI 兼容接口的固定前缀（真正的接口是 /v1/embeddings）
        return f"http://{self._config.host}:{self._config.port}/v1"

    def get_client(self):  # 创建并返回一个"向量化客户端"（此时只是准备好参数，不会立刻发请求）
        return OpenAIEmbeddings(  # 造一个 OpenAI 兼容的 embedding 客户端
            base_url=self._url,  # 请求发给我们自部署的 TEI，而不是真正的 OpenAI
            # api_key 是必填项，但 TEI 默认不校验，所以随便填 "unused"
            api_key="unused",  # TEI does not require authentication by default
            check_embedding_ctx_length=False,  # 关掉"先在本地按 token 长度切分/截断"的检查，原样把文字发给服务端
        )
