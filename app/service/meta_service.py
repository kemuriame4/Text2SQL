import datetime

from app.client.mysql_client import MysqlClient
from app.conf.app_config import app_config
from app.conf.meta_config import MetaConfig, TableConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql.dw.dw_mysql_repository import DwMysqlRepository
from app.repository.mysql.meta.column_info_mysql_repository import ColumnInfoMysqlRepository
from app.repository.mysql.meta.table_info_mysql_repository import TableInfoMysqlRepository
from app.utils.load_config_util import load_config
from app.utils.log_util import logger

# yaml 中的表角色名 -> t_table_info.role(CHAR 1) 的编码
_ROLE_MAP = {'dim': '0', 'fact': '1'}
# 每列从 dw 库抽取的示例条数
_EXAMPLES_LIMIT = 3


class MetaService:
    def __init__(self):
        self._table_info_mysql_repository: TableInfoMysqlRepository | None = None
        self._dw_mysql_repository: DwMysqlRepository | None = None
        self._column_info_mysql_repository: ColumnInfoMysqlRepository | None = None

    async def _sync_tables(self, tables: list[TableConfig]):
        """同步表信息到 t_table_info：已存在则更新，否则新增。"""
        repo = self._table_info_mysql_repository
        now = datetime.datetime.now()
        add_list: list[TableInfoEntity] = []
        update_list: list[TableInfoEntity] = []

        for table in tables:
            table_info = TableInfoEntity(
                id=table.name,
                name=table.name,
                role=_ROLE_MAP.get(table.role, table.role),
                description=table.description,
                create_time=now,
                create_by='meta_init',
                update_time=now,
                update_by='meta_init',
            )
            raw_table = await repo.get_table_info_by_id(table_info.id)
            if raw_table:
                update_list.append(table_info)
            else:
                add_list.append(table_info)

        if update_list:
            await repo.batch_update_table_infos(update_list)
        if add_list:
            await repo.batch_add_table_info(add_list)

    async def _sync_columns(self, tables: list[TableConfig]):
        """同步列信息到 t_column_info：类型/示例从 dw 库反查，已存在则更新，否则新增。"""
        column_repo = self._column_info_mysql_repository
        dw_repo = self._dw_mysql_repository
        now = datetime.datetime.now()
        add_list: list[ColumnInfoEntity] = []
        update_list: list[ColumnInfoEntity] = []

        for table in tables:
            types: dict[str, str] = await dw_repo.get_type_by_name(table.name)
            for column in table.columns:
                column_type = types.get(column.name)
                if column_type is None:
                    logger.warning(f'dw 表 {table.name} 中不存在列 {column.name}，type 置为空字符串')
                    column_type = ''
                examples = await dw_repo.get_examples_by_name(
                    table.name, column.name, _EXAMPLES_LIMIT
                )
                column_info = ColumnInfoEntity(
                    id=f'{table.name}.{column.name}',
                    name=column.name,
                    type=column_type,
                    role=column.role,
                    examples=examples,
                    description=column.description,
                    alias=list(column.alias),
                    table_id=table.name,
                    create_time=now,
                    create_by='meta_init',
                    update_time=now,
                    update_by='meta_init',
                )
                raw_column = await column_repo.get_column_info_by_id(column_info.id)
                if raw_column:
                    update_list.append(column_info)
                else:
                    add_list.append(column_info)

        if update_list:
            await column_repo.batch_update_column_infos(update_list)
        if add_list:
            await column_repo.batch_add_column_info(add_list)

    async def build(self, file_path: str):
        meta_config: MetaConfig = load_config(file_path, schema=MetaConfig)
        meta_mysql_client = MysqlClient(app_config.db_meta)
        dw_mysql_client = MysqlClient(app_config.db_dw)
        try:
            meta_factory = meta_mysql_client.get_session_factory()
            dw_factory = dw_mysql_client.get_session_factory()

            async with meta_factory() as meta_session, dw_factory() as dw_session:
                self._table_info_mysql_repository = TableInfoMysqlRepository(meta_session)
                self._dw_mysql_repository = DwMysqlRepository(dw_session)
                self._column_info_mysql_repository = ColumnInfoMysqlRepository(meta_session)

                if meta_config and meta_config.tables:
                    # 事务边界由 Service 层管理，Repository 不再暴露私有 session
                    async with meta_session.begin():
                        await self._sync_tables(meta_config.tables)
                        await self._sync_columns(meta_config.tables)
                    logger.info(f'元数据同步完成，共处理 {len(meta_config.tables)} 张表')
                else:
                    logger.warning('meta 配置为空，未同步任何表信息')
        finally:
            await meta_mysql_client.close()
            await dw_mysql_client.close()
