from app.client.mysql_client import CustomMysqlClient
from app.conf.app_config import appConfig
from app.conf.meta_config import MetaConfig,TableConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql import column_info_mysql_repository
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.dw import dw_mysql_repository
from app.repository.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.utils.load_config_util import load_config

class MetaService:
    def __init__(self):
        pass

    async def _save_tables_to_mysql(self,tables:list[TableConfig]):
        async with self._table_info_mysql_repository.session.begin():
            tableInfos = []
            updateTableInfos = []
            columnInfos = []
            updateColumnInfos = []
            for table in tables:
                tableInfo = TableInfoEntity(
                    id = table.name,
                    name = table.name,
                    description = table.description,
                    role = table.role
                )
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if rowTable is not None:
                    updateTableInfos.append(tableInfo)
                else:
                    tableInfos.append(tableInfo)

                types = await self._dw_mysql_repository.get_column_type_by_name(table.name)

                for column in table.columns:
                    examples = await self._dw_mysql_repository.get_column_values(table.name, column.name)
                    columnInfo = ColumnInfoEntity(
                        id = f'{table.name}.{column.name}',
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
                        updateColumnInfos.append(columnInfo)
                    else:
                        columnInfos.append(columnInfo)

            if len(updateTableInfos) > 0:
                await self._table_info_mysql_repository.batch_update_table_infos(updateTableInfos)
            if len(tableInfos) > 0:
                await self._table_info_mysql_repository.batch_add_table_infos(tableInfos)
            if len(updateColumnInfos)> 0:
                await self._column_info_mysql_repository.batch_update_column_infos(updateColumnInfos)
            if len(columnInfos) > 0:
                await self._column_info_mysql_repository.batch_add_column_infos(columnInfos)
        return columnInfos+updateColumnInfos

    async def build(self,file_path:str):
        '''
        file_path:元数据的配置文件的地址
        '''

        #加载配置文件
        meta_config:MetaConfig = load_config(file_path,MetaConfig)

        meta_mysql_client = CustomMysqlClient(appConfig.db_meta)
        dw_mysql_client = CustomMysqlClient(appConfig.db_dw)

        meta_mysql_client.get_session_factory()
        dw_mysql_client.get_session_factory()

        async with meta_mysql_client.sessionFactory() as meta_session,dw_mysql_client.sessionFactory() as dw_session:
            self._column_info_mysql_repository = ColumnInfoMySqlRepository(meta_session)
            self._table_info_mysql_repository = TableInfoMySqlRepository(meta_session)
            self._dw_mysql_repository = DwMysqlRepository(dw_session)

            if meta_config is not None and meta_config.tables is not None:

                # 将tables数据解析并且写入到mysql数据库中
                columnInfos = await self._save_tables_to_mysql(meta_config.tables)
                print('columnsInfo数据为:',columnInfos)