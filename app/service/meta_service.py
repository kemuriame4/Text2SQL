from loguru import logger

from app.client.mysql_client import CustomMySqlClient
from app.conf.app_config import  appConfig
from app.conf.meta_config import MetaConfig, TableConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.dw.dw_mysql_repostory import DwMysqlRepostory
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.utils.load_config_util import load_config


class MetaService:
    def __init__(self):
        # 三个仓储对象在 build() 里创建，先声明出来避免"属性突然冒出来"
        self._table_info_mysql_repository: TableInfoMySqlRepository | None = None
        self._column_info_mysql_repository: ColumnInfoMySqlRepository | None = None
        self._dw_mysql_repostory: DwMysqlRepostory | None = None

    async def _save_tables_to_mysql(self, tables: list[TableConfig]):
        # 开启会话
        async  with self._table_info_mysql_repository.session.begin():
            # 将TableConfig转换为TableInfoEntity和ColumnInfoEntity
            tableInfos = []
            updateTableInfos = []
            columnInfos = []
            updateColumnInfos = []
            # 循环表信息
            for table in tables:
                # 构建表信息
                tableInfo = TableInfoEntity(
                    id= table.name,
                    name= table.name,
                    description= table.description,
                    role= table.role,
                )
                # 查询数据是否存在：存在 -> 待更新，不存在 -> 待新增
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if rowTable is not None:
                    updateTableInfos.append(tableInfo)
                else:
                    # 【原代码的 bug】这里写成了 columnInfos.append(tableInfo)，
                    # 把"表实体"塞进了"字段列表"，插入时会往 t_column_info 里插一条 id=表名的脏数据
                    tableInfos.append(tableInfo)
                # type 从数据仓库中获取字段的数据类型
                types =await self._dw_mysql_repostory.get_column_type_by_name(table.name)

                for column in table.columns:
                    # examples 从数据仓库中获取数据
                    examples = await  self._dw_mysql_repostory.get_column_values(table.name,column.name)
                    # 构建字段的对象数据
                    columnInfo = ColumnInfoEntity(
                        id = f'{table.name}.{column.name}',
                        name= column.name,
                        description= column.description,
                        role= column.role,
                        alias= column.alias,
                        # 从字典中获取数据类型；用 get 兜底，数仓里查不到的字段不会直接 KeyError 崩掉
                        type=types.get(column.name),
                        examples=examples,
                        table_id= table.name
                    )
                    # 判断字段是否存在
                    rowColumn = await self._column_info_mysql_repository.get_column_info_by_id(columnInfo.id)
                    if rowColumn is not None:
                        updateColumnInfos.append(columnInfo)
                    else:
                        columnInfos.append(columnInfo)

            # 【原代码的 bug】原来写的是 if 更新 else 新增 —— 只要有一条已存在，
            # 所有"新增"的数据就被整个丢掉了，而且 tableInfos 永远为空。
            # 正确做法：新增和更新各自独立判断。
            if len(tableInfos) > 0:
                await self._table_info_mysql_repository.batch_add_table_infos(tableInfos)
            if len(updateTableInfos) > 0:
                await self._table_info_mysql_repository.batch_update_table_infos(updateTableInfos)
            if len(columnInfos) > 0:
                await self._column_info_mysql_repository.batch_add_column_infos(columnInfos)
            if len(updateColumnInfos) > 0:
                await self._column_info_mysql_repository.batch_update_column_infos(updateColumnInfos)

            # 立刻 flush，让主键冲突/非空约束在这里就暴露，而不是等到 commit
            await self._table_info_mysql_repository.session.flush()
        # 返回所有字段的信息列表
        return columnInfos+updateColumnInfos

    async def build(self,file_path:str):
        '''
        :param file_path:  元数据配置文件的地址
        :return:
        '''
        # 加载配置文件 -> MetaConfig 业务实体
        meta_config : MetaConfig= load_config(file_path,MetaConfig)
        logger.info(f'元数据配置文件加载完成：{len(meta_config.tables)} 张表、{len(meta_config.metrics)} 个指标')

        meta_mysql_client = CustomMySqlClient(appConfig.db_meta)
        dw_mysql_client = CustomMySqlClient(appConfig.db_dw)

        meta_factory = meta_mysql_client.get_session_factory()
        dw_factory = dw_mysql_client.get_session_factory()
        async  with meta_factory() as meta_session, dw_factory() as dw_session:
            self._column_info_mysql_repository =ColumnInfoMySqlRepository(meta_session)
            self._table_info_mysql_repository =TableInfoMySqlRepository(meta_session)
            self._dw_mysql_repostory = DwMysqlRepostory(dw_session)


            if meta_config is not None and meta_config.tables is not None:
                # 将tables数据解析并且写入到mysql数据库中
                columnInfos = await  self._save_tables_to_mysql(meta_config.tables)
                logger.info(f'字段信息写入完成，共 {len(columnInfos)} 个字段')

            # 提示：meta_config.metrics 目前还没有落库（t_metric_info / t_column_metric 表已建好）
            if meta_config is not None and meta_config.metrics:
                logger.warning(f'检测到 {len(meta_config.metrics)} 个指标，当前版本的 MetaService 尚未写入指标表')
            return columnInfos if meta_config is not None and meta_config.tables else []
