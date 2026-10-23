import uuid

from app.client.custom_embedding_client import CustomEmbeddingClient
from app.client.custom_qdrant_client import CustomQdrantClient
from app.client.mysql_client import CustomMysqlClient
from app.conf.meta_config import TableConfig, MetaConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.dw.dw_mysql_repository import DWMysqlRepository
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.utils.load_config import load_config
from app.conf.app_config import AppConfig


class MetaService:
    def __init__(self):
        pass

    async def _save_tables_to_mysql(self,tables:list[TableConfig]):
        # 开启会话
        async with self._table_info_mysql_repository._session.begin():
            # 将TableConfig转换为TableInfoEntity和ColumnInfoEntity
            tableInfos = []
            updateTableInfos = []
            columnInfos = []
            updateColumnInfos = []

            # 循环表信息
            for table in tables:
                # 构建表信息
                tableInfo = TableInfoEntity(
                    id=table.name,
                    name=table.name,
                    description=table.description,
                    role=table.role,
                )
                # 将数据添加到列表中
                # 查询数据是否存在
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if rowTable is not None:
                    updateTableInfos.append(tableInfo)
                else:
                    tableInfos.append(tableInfo)
                # type从数据仓库中获取字段的数据类型
                types = await self._dw_mysql_repository.get_column_type_by_name(table.name)
                for column in table.columns:
                    # examples 从数据仓库中获取数据
                    examples = await self._dw_mysql_repository.get_column_values(table.name, column.name)
                    # 构建字段的对象数据
                    columnInfo = ColumnInfoEntity(
                        id = f'{table.name}.{column.name}',
                        name = column.name,
                        description = column.description,
                        role = column.role,
                        alias = column.alias,
                        # 从字典中获取数据类型
                        type = types[column.name],
                        table_id = table.name
                    )
                    rowColumn = await self._column_info_mysql_repository.get_column_info_by_id(columnInfo.id)
                    if rowColumn is not None:
                        updateColumnInfos.append(columnInfo)
                    else:
                        columnInfos.append(columnInfo)

            # 校验是否存在
            if len(updateTableInfos) > 0:
                await self._table_info_mysql_repository.batch_update_table_info(updateTableInfos)
            if len(tableInfos) > 0:
                await self._table_info_mysql_repository.batch_add_table_info(tableInfos)
            if len(updateColumnInfos) > 0:
                await self._column_info_mysql_repository.batch_update_column_info(updateColumnInfos)
            if len(columnInfos) > 0:
                await self._column_info_mysql_repository.batch_add_column_info(columnInfos)

            # 返回所有字段的信息列表
            return columnInfos+updateColumnInfos

    async def _save_columns_to_qdrant(self,column_infos:list[ColumnInfoEntity]):
        # 创建集合
        await self._column_qdrant_repository.create_collection()
        points:list[dict] = []
        for columnInfo in column_infos:
            i :int = 0
            points.append({
                'id':uuid.uuid4(),
                'embedding_text':columnInfo.name,
                'payload':columnInfo
            })
            i += 1
            points.append({
                'id':uuid.uuid4(),
                'embedding_text':columnInfo.description,
                'payload':columnInfo
            })
            for alias in columnInfo.alias:
                i += 1
                points.append({
                    'id':uuid.uuid4(),
                    'embedding_text':alias,
                    'payload':columnInfo
                })

            embedding_texts = [point['embedding_text'] for point in points]
            ids = [point['id'] for point in points]
            payloads = [point['payload'] for point in points]
            embeddings = []
            # 将embedding_text向量化
            batch_embedding = 20
            for i in range(0,len(embedding_texts),batch_embedding):
                batch_embedding_texts = embedding_texts[i:i+batch_embedding]
                batch_embeddings = await self._embedding_client.aembed_documents(batch_embedding_texts)
                embeddings.extend(batch_embeddings)
            await self._column_qdrant_repository.insert_and_update(ids,embeddings,payloads)

    async def build(self,file_path:str):
        # 加载配置文件
        meta_config:MetaConfig = load_config(file_path,MetaConfig)

        meta_mysql_client = CustomMysqlClient(AppConfig.db_meta)
        dw_mysql_client = CustomMysqlClient(AppConfig.db_dw)

        meta_mysql_client.get_session_factory()
        dw_mysql_client.get_session_factory()

        # 获取qdrant连接
        qdrant_client = CustomQdrantClient(AppConfig.qdrant)
        qdrant_client.get_client()

        self._embedding_client = CustomEmbeddingClient(AppConfig.embedding).get_client()

        # 实例化数据交互层ColumnQdrantRepository
        async with meta_mysql_client.sessionFactory() as meta_session,dw_mysql_client.sessionFactory() as dw_session:
            self._column_info_mysql_repository = ColumnInfoMySqlRepository(meta_session)
            self._table_info_mysql_repository = TableInfoMySqlRepository(meta_session)
            self._dw_mysql_repository = DWMysqlRepository(dw_session)
            self._column_qdrant_repository = ColumnQdrantRepository(qdrant_client.client,AppConfig.embedding.embedding_size)

            if meta_config is not None and meta_config.tables is not None:
                # 将tables数据解析并且写入到mysql数据库中
                columnInfos = await self._save_tables_to_mysql(meta_config.tables)
                print('columnsInfo数据为:',columnInfos)
                # 将字段信息写入到qdrant
                await self._save_columns_to_qdrant(columnInfos)

