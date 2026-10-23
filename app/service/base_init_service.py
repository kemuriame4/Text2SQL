
from sqlalchemy import alias, update

from app.client.custom_qdrant_client import CustomQdrantClient
from app.client.mysql_client import CustomMysqlClient
from app.conf.mate_config import MateConfig
from app.conf.mate_config import TableConfig

from app.conf.app_config import appConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.column_info_repository import ColumnInfoMySqlRepository
from app.repository.dw_repository import DwMysqlRepostory
from app.repository.table_info_repository import TableInfoMySqlRepository
from app.utils.load_config_util import load_config


class BaseInitService:
    def __init__(self):
        pass

    async def _save_table_tomysql(self, tables: list[TableConfig]):
        """
        保存表信息到数据库
        :param table_info: 表信息对象
        :return: None
        """
        async with self._table_info_mysql_repository.begin():
            tableInfos = []
            updateTableInfos = []
            columnInfos  = []
            updateColumnInfos = []
            for table in tables:
                tableInfo = TableInfoEntity(
                    id = table.name,
                    name = table.name,
                    description = table.description,
                    role = table.role,
                )
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if rowTable is not None:
                    updateTableInfos.append(tableInfo)
                else:
                    tableInfos.append(tableInfo)
                types = await self._dw_mysql_repository.get_column_type_by_name(tableInfo.name)
                for column in table.columns:
                    examples = await self._dw_mysql_repository.get_column_values(table.name,column.name)
                    columnInfo = ColumnInfoEntity(
                        id = f"{tableInfo.name}.{column.name}",
                        name = column.name,
                        description = column.description,
                        role = column.role,
                        alias = column.alias,
                        type = types[column.name],
                        examples = examples,
                        table_id = table.name
                    )
                    rowColumn = await self._column_info_mysql_repository.get_column_info_by_id(columnInfo.id)
                    if rowColumn is not None:
                        updateColumnInfos.append(rowColumn)
                    else:
                        columnInfos.append(rowColumn)
            if len(updateTableInfos) >  0:
                await self._table_info_mysql_repository.batch_update_table_infos(updateTableInfos)
            if len(tableInfos) >  0:
                await  self._table_info_mysql_repository.batch_add_table_infos(tableInfos)
            if len(updateColumnInfos) > 0:
                await self._column_info_mysql_repository.batch_update_column_infos(updateColumnInfos)
            if len(columnInfos) > 0:
                await self._column_info_mysql_repository.batch_add_column_infos(columnInfos)

    async def _save_colums_to_qdrant(self,column_infos:list[ColumnInfoEntity]):
        await self._column_info_qdrant_repository
        pass

    async def build(self,file_path:str):
        """
        初始化元数据
        :param file_path: 配置文件路径
        :return: None
        """
        meta_config:MateConfig = load_config(file_path,MateConfig)
        meta_mysql_client = CustomMysqlClient(appConfig.db_meta)
        dw_mysql_client = CustomMysqlClient(appConfig.db_dw)

        # 获取qdrant连接
        qdrant_client = CustomQdrantClient(appConfig.qdrant)
        qdrant_client.get_client()

        # self._embedding_client = CustomEmbeddingClient(appConfig.embedding).get_client()
        
        async with meta_mysql_client.sessionLocal() as meta_session,dw_mysql_client.sessionLocal() as dw_session:
            self._column_info_mysql_repository = ColumnInfoMySqlRepository(meta_session)
            self._table_info_mysql_repository = TableInfoMySqlRepository(meta_session)
            self._dw_mysql_repository = DwMysqlRepostory()

            if meta_config is not None and meta_config.tables is not None:
                columninfos = await self._save_table_tomysql(meta_config.tables)
                print('columnsInfo数据为：',columninfos)

                # await self._save_colums_to_qdrant(columninfos)