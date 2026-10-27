from personal.utils.config_loader import load_config
import uuid
from personal.repository.ElasticSearch.column_ElasticSearch_repository import (
    ColumnElasticSearchRepository,
)
from personal.repository.Qdrant.metric_Qdrant_repository import MetricQdrantRepository
from personal.repository.MySQL.column_MySQL_repository import (
    ColumnMetricMySQLRepository,
)
from personal.repository.Qdrant.column_Qdrant_repository import ColumnQdrantRepository
from personal.repository.MySQL.dw.dw_MySQL_repository import DwMySQLRepository
from personal.repository.MySQL.info_MySQL_repository import (
    TableInfoMySQLRepository,
    MetricMySQLRepository,
)
from personal.repository.MySQL.column_MySQL_repository import ColumnInfoMySQLRepository
from personal.client.embedding_client import CustomEmbeddingClient
from personal.client.qdrant_client import CustomQdrantClient
from personal.client.mysql_client import CustomMysqlClient
from personal.config.app_config import app_config
from personal.config.meta_config import (
    MetaConfig,
    TableConfig,
    MetricConfig,
)
from personal.entity.column_entity import ColumnInfoEntity
from personal.entity.info_entity import TableInfoEntity, MetricInfoEntity


class MetaService:
    def __init__(self):
        pass

    async def build(self, file_path: str):
        meta_config: MetaConfig = load_config(file_path, MetaConfig)

        meta_MySQL_client = CustomMysqlClient(app_config.database_meta)
        dw_MySQL_client = CustomMysqlClient(app_config.database_dw)
        meta_session_factory = meta_MySQL_client.get_session_factory()
        dw_session_factory = dw_MySQL_client.get_session_factory()

        qdrant_client = CustomQdrantClient(app_config.qdrant)
        qdrant_client.get_client()

        self._embedding_client = CustomEmbeddingClient(app_config.embedding)
        self._embedding_client.get_client()

        self._es_client = CustomEmbeddingClient(app_config.elastic_search)
        self._es_client.get_client()

        async with (
            meta_MySQL_client.sessionFactory() as meta_session,
            dw_MySQL_client.sessionFactory() as dw_session,
        ):
            self._conlumn_info_MySQL_repository = ColumnInfoMySQLRepository(
                meta_session
            )
            self._table_info_MySQL_repository = TableInfoMySQLRepository(meta_session)
            self._column_metric_MySQL_repository = ColumnMetricMySQLRepository(
                meta_session
            )
            self._metric_info_MySQL_repository = MetricMySQLRepository(meta_session)

            self._dw_mysql_repository = DwMySQLRepository(dw_session)
            self._column_qdrant_repository = ColumnQdrantRepository(
                qdrant_client.client, app_config.embedding.embedding_size
            )
            self._metric_qdrant_repository = MetricQdrantRepository(
                qdrant_client.client, app_config.embedding.embedding_size
            )
            self._cloumn_es_repository = ColumnElasticSearchRepository(
                self._es_client.client
            )

        if meta_config is not None and meta_config.metrics is not None:
            metric_infos = await self._save_metrics_to_MySQL(meta_config.metrics)
            await self._save_metrics_to_Qrant(metric_infos)

    async def _save_tables_to_mysql(self, tables: list[TableConfig]):
        async with self._table_info_mysql_repository.session.begin():
            table_infos = []
            update_table_infos = []
            column_infos = []
            update_column_infos = []
            for table in tables:
                table_info = TableInfoEntity(
                    id=table.name,
                    name=table.name,
                    description=table.description,
                    role=table.role,
                )

                row_table = (
                    await self._table_info_mysql_repository.get_table_info_by_id(
                        table_info.id
                    )
                )
                if row_table is not None:
                    update_table_infos.append(table_info)
                else:
                    table_infos.append(table_info)

                types = await self._dw_mysql_repository.get_column_type_by_name(
                    table.name
                )

                for column in table.columns:
                    examples = await self._dw_mysql_repository.get_column_values(
                        table.name, column.name
                    )

                    column_info = ColumnInfoEntity(
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        description=column.description,
                        role=column.role,
                        alias=column.alias,
                        type=types[column.name],
                        examples=examples,
                        table_id=table.name,
                    )

                    row_column = (
                        await self._column_info_mysql_repository.get_column_info_by_id(
                            column_info.id
                        )
                    )
                    if row_column is not None:
                        update_column_infos.append(column_info)
                    else:
                        column_infos.append(column_info)

                # if len(update_table_infos) > 0:
                #     await self._table_info_mysql_repository.batch_update_table_infos(
                #         update_table_infos
                #     )
                # if len(table_infos) > 0:
                #     await self._table_info_mysql_repository.batch_add_table_infos(
                #         table_infos
                #     )
                # if len(update_column_infos) > 0:
                #     await self._column_info_mysql_repository.batch_update_column_infos(
                #         update_column_infos
                #     )
                # if len(column_infos) > 0:
                #     await self._column_info_mysql_repository.batch_add_column_infos(
                #         column_infos
                #     )

            return column_infos + update_column_infos

    async def _save_columns_to_Qrant(self, column_infos: list[ColumnInfoEntity]):
        await self._column_qdrant_repository.create_collection()
        points: list[dict] = []
        for columnInfo in column_infos:
            i = 0
            points.append(
                {
                    "id": uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"{columnInfo.table_id}.{columnInfo.name}.{i}",
                    ),
                    "embedding_text": columnInfo.name,
                    "payload": columnInfo,
                }
            )
            i += 1
            points.append(
                {
                    "id": uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"{columnInfo.table_id}.{columnInfo.name}.{i}",
                    ),
                    "embedding_text": columnInfo.description,
                    "payload": columnInfo,
                }
            )

            for alias in columnInfo.alias:
                i += 1
                points.append(
                    {
                        "id": uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"{columnInfo.table_id}.{columnInfo.name}.{i}",
                        ),
                        "embedding_text": alias,
                        "payload": columnInfo,
                    }
                )

            embedding_texts = [point["embedding_text"] for point in points]
            ids = [point["id"] for point in points]
            payloads = [point["payload"] for point in points]
            embeddings = []

            batch_embedding = 20
            for i in range(0, len(embedding_texts), batch_embedding):
                batch_embedding_texts = embedding_texts[i : i + batch_embedding]
                batch_embeddings = await self._embedding_client.aembed_documents(
                    batch_embedding_texts
                )
                embeddings.extend(batch_embeddings)

            await self._column_qdrant_repository.insert_and_update(
                ids, embeddings, payloads
            )

    async def _save_metrics_to_MySQL(self, metrics: list[MetricConfig]):
        pass

    async def _save_metrics_to_Qrant(self, metric_infos: list[MetricInfoEntity]):
        pass
