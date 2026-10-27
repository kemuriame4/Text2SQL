# 【文件作用】
# 这个文件负责把"字段信息"写进 / 读出自 Qdrant 向量库（存向量的数据库，可以按"意思相近"来检索）。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 写：把字段文字对应的向量 + 附加信息存进去；读：拿一个查询向量去找最相似的那几条字段。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from qdrant_client import AsyncQdrantClient  # 异步的 Qdrant 客户端（负责和向量库通信）

from qdrant_client.http.models import Distance, VectorParams, PointStruct  # Distance 距离算法；VectorParams 向量参数；PointStruct 一条向量记录（点）

from app.entity.column_info_entity import ColumnInfoEntity  # 字段信息实体（这里既当写入的 payload，也当查询结果的容器）


class ColumnQdrantRepository:  # 定义"字段向量仓库"类
    _collection_name = 'column_qdrant_oy'  # collection（向量库里的"集合"，相当于一张表）的名字，_oy 后缀用来和其他环境区分
    def __init__(self, client:AsyncQdrantClient,size:int = 1024):  # 构造方法：传入客户端 + 向量维度（默认 1024）
        self._client = client  # 存下客户端，后面每个方法都用它和向量库通信
        self._size = size  # 存下向量维度（这串数字有几个数字，项目里是 1024 个）

    async  def create_collection(self):  # 创建集合（如果还不存在）
        if not await self._client.collection_exists(self._collection_name):  # 先问一下集合是否已存在，不存在才创建（幂等：重复做结果一样，不会多出一份）
            await self._client.create_collection(  # 创建集合
                self._collection_name,  # 集合名
                vectors_config= VectorParams(size=self._size, distance=Distance.DOT)  # 向量参数：维度 1024；相似度用点积 DOT（两个向量越像，点积越大）
            )

    async def insert_and_update(self,ids:list[str],embeddings:list[list[float]],payloads: list[ColumnInfoEntity],batch_size: int = 20):  # 批量写入 / 更新向量（upsert = 有就更新、没有就插入）
        zipped = list(zip(ids,embeddings,payloads))  # 把 id、向量、payload 三组数据按位置一一配对成 (id, 向量, payload)
        #分批处理数据
        for i in range(0, len(zipped), batch_size):  # 每次跳 batch_size 步，把数据切成一批一批
            batch = zipped[i:i+batch_size]  # 取出当前这一批
            # payload 参数为字典，所以需要将payload转asdict(payload)
            # 【注意】Qdrant 的 point id 只接受 UUID 字符串或整数，如果业务 id 是别的格式，写入会报错
            batch_points = [PointStruct(id=id,vector=embedding,payload=asdict(payload)) for id,embedding,payload in batch]  # 每条转成 PointStruct（Qdrant 要求的格式）；payload（跟着向量一起存进去的附加信息）要转成字典
            await self._client.upsert(collection_name=self._collection_name,points=batch_points)  # 把这批点一次性写进集合

    async  def search(self,embedding:list[float],score_threshold:float=0.5,limit:int=5):  # 拿查询向量做相似度检索
        result = await self._client.query_points(  # 发起检索
            collection_name=self._collection_name,  # 在哪个集合里找
            query=embedding,  # 查询用的向量（比如把用户那句话也转成向量）
            score_threshold=score_threshold,  # 分数低于这个阈值的直接丢掉
            limit=limit  # 最多返回几条
        )
        return [ColumnInfoEntity(**point.payload) for point in result.points]  # 把每条结果的 payload 字典还原成字段实体，组成列表返回
