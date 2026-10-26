from dataclasses import asdict

from qdrant_client import AsyncQdrantClient

from qdrant_client.http.models import Distance, VectorParams, PointStruct

from app.entity.column_info_entity import ColumnInfoEntity


class ColumnQdrantRepository:
    _collection_name = 'column_qdrant_oy'
    def __init__(self, client:AsyncQdrantClient,size:int = 1024):
        self._client = client
        self._size = size

    async  def create_collection(self):
        if not await self._client.collection_exists(self._collection_name):
            await self._client.create_collection(
                self._collection_name,
                vectors_config= VectorParams(size=self._size, distance=Distance.DOT)
            )

    async def insert_and_update(self,ids:list[str],embeddings:list[list[float]],payloads: list[ColumnInfoEntity],batch_size: int = 20):
        zipped = list(zip(ids,embeddings,payloads))
        #分批处理数据
        for i in range(0, len(zipped), batch_size):
            batch = zipped[i:i+batch_size]
            # payload 参数为字典，所以需要将payload转asdict(payload)
            batch_points = [PointStruct(id=id,vector=embedding,payload=asdict(payload)) for id,embedding,payload in batch]
            await self._client.upsert(collection_name=self._collection_name,points=batch_points)

    async  def search(self,embedding:list[float],score_threshold:float=0.5,limit:int=5):
        result = await self._client.query_points(
            collection_name=self._collection_name,
            query=embedding,
            score_threshold=score_threshold,
            limit=limit
        )
        return [ColumnInfoEntity(**point.payload) for point in result.points]
