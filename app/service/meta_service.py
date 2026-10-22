from app.client.mysql_client import MysqlClient
from app.conf.meta_config import MetaConfig
from app.conf.app_config import app_config
from app.conf.meta_config import TableConfig
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repository.mysql.meta.table_info_mysql_repository import TableInfoMysqlRepository
from app.utils.load_config_util import load_config


class MetaService:
    def __init__(self):
        pass

    async def _save_tabl_to_mysql(self, tables: list[TableConfig]):
        async with self._table_info_mysql_repository._session.begin():
            tableInfos = []
            updateTableInfos = []
            columnsInfos = []
            updateColumnsInfos = []
            # 循环表信息
            for table in tables:
                tableInfo = TableInfoEntity(
                    id=table.name,
                    name=table.name,
                    role=table.role,
                    description=table.description
                )
                raw_table = await  self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if raw_table:
                    updateTableInfos.append(tableInfo)
                tableInfos.append(tableInfo)
            if len(updateTableInfos) > 0:
                await self._table_info_mysql_repository.batch_update_table_infos(tableInfos)
            else :
                await self._table_info_mysql_repository.batch_add_table_info(tableInfos)


    async def build(self, file_path: str):
        meta_config: MetaConfig = load_config(file_path)
        meta_mysql_client = MysqlClient(app_config.db_meta)
        dw_mysql_client = MysqlClient(app_config.db_dw)
        meta_mysql_client.get_session_factory()
        dw_mysql_client.get_session_factory()

        async with meta_mysql_client.sessionFactory() as meta_session, dw_mysql_client.sessionFactory() as dw_session:
            self._table_info_mysql_repository = TableInfoMysqlRepository(meta_session)
            self._dw_mysql_repository = DwMysqlRepository(dw_session)
            if not meta_config or not meta_config.tables:
                await  self._save_tabl_to_mysql(meta_config.tables)
