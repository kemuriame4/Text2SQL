from dataclasses import asdict
from elasticsearch import AsyncElasticsearch
from personal.entity.base_entity import ValueInfo


class ColumnElasticSearchRepository:
    _index_name = "column_es_kemuriame"
    _index_mapping = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
            },
            "column_id": {"type": "keyword"},
        },
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def create_index(self):
        if not await self.client.indices.exists(index=self._index_name):
            await self.client.indices.create(
                index=self._index_name, mappings=self._index_mapping
            )

    async def insert_index(self, values: list[ValueInfo], batch_size: int = 20):
        for i in range(0, len(values), batch_size):
            batch = values[i : i + batch_size]
            operations = []
            for value in batch:
                operations.append(
                    {"index": {"_index": self._index_name}, "_id": value.id}
                )
                operations.append(asdict(value))
            await self.client.bulk(operations=operations)
