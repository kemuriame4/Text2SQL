"""元数据构建服务：读 meta_config.yaml，从数据仓库补齐类型和示例值，再写入元数据库。"""
from app.client.mysql_client import CustomMySqlClient
from app.conf.app_config import  appConfig
from app.conf.meta_config import MetaConfig, TableConfig
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.repository.mysql import column_info_mysql_repository
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository
from app.repository.mysql.dw import dw_mysql_repostory
from app.repository.mysql.dw.dw_mysql_repostory import DwMysqlRepostory
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository
from app.utils.load_config_util import load_config


class MetaService:
    """整个项目唯一做"业务判断"的地方：哪些数据新增、哪些更新、字段该填什么。"""

    def __init__(self):
        """
        做什么：空构造函数。
        参数：无。
        返回：无。
        注意：三个 repository（self._column_info_mysql_repository 等）不在这里创建，
        而是在 build() 里才赋值。所以在 build() 之前调用 _save_tables_to_mysql 会 AttributeError。
        """
        pass

    async def _save_tables_to_mysql(self, tables: list[TableConfig]):
        """
        做什么：把配置里的表清单和字段清单写成元数据库记录（存在则更新、不存在则新增）。
        参数：
        tables (list[TableConfig])：来自 meta_config.yaml 的表声明列表，每项含字段列表。
        返回：
        list[ColumnInfoEntity]：本次处理过的**所有**字段实体（新增的在前，更新的在后）。
        tables 为空时返回空列表。
        注意：① 事务由 self._table_info_mysql_repository.session.begin() 控制，
                方法正常结束时自动提交，中途抛异常则整批回滚；
              ② 新增和更新是二选一：只要本次里存在任何一条要更新的记录，
                同一批里新增的记录就不会被写进去（见下方 if/else）；
              ③ 一个字段要发 3 条 SQL（查类型、取示例、查是否已存在），表越多越慢。
        """
        # 开启会话
        async  with self._table_info_mysql_repository.session.begin():
            # 将TableConfig转换为TableInfoEntity和ColumnInfoEntity
            tableInfos = []          # 待新增的表
            updateTableInfos = []    # 待更新的表
            columnInfos = []         # 待新增的字段
            updateColumnInfos = []   # 待更新的字段
            # 循环表信息
            for table in tables:
                # 构建表信息
                tableInfo = TableInfoEntity(
                    id= table.name,          # 表名当主键，保证重跑幂等
                    name= table.name,
                    description= table.description,
                    role= table.role,
                )
                # 将数据添加到列表中
                # 查询数据是否存在
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)
                if rowTable is not None:
                    updateTableInfos.append(tableInfo)
                else:
                    tableInfos.append(tableInfo)
                # tableInfos.append(tableInfo)
                # type 从数据仓库中获取字段的数据类型
                types =await self._dw_mysql_repostory.get_column_type_by_name(table.name)

                for column in table.columns:
                    # examples 从数据仓库中获取数据
                    examples = await  self._dw_mysql_repostory.get_column_values(table.name,column.name)
                    # 构建字段的对象数据
                    columnInfo = ColumnInfoEntity(
                        id = f'{table.name}.{column.name}',   # 表名.字段名，字段级主键
                        name= column.name,
                        description= column.description,
                        role= column.role,
                        alias= column.alias,
                        # 从字典中获取数据类型
                        type=types[column.name],   # 数仓里查不到该列会抛 KeyError
                        examples=examples,
                        table_id= table.name
                    )
                    # 判断字段是否存在
                    rowColumn = await self._column_info_mysql_repository.get_column_info_by_id(columnInfo.id)
                    if rowColumn is not None:
                        updateColumnInfos.append(columnInfo)
                    else:
                        columnInfos.append(columnInfo)

            #  校验是否存在，
            # 注意：这里是 if/else 互斥，表或字段"既有新增又有更新"时，新增部分会被整批跳过
            if len(updateTableInfos) > 0:
                await self._table_info_mysql_repository.batch_update_table_infos(updateTableInfos)
            else:
                await  self._table_info_mysql_repository.batch_add_table_infos(tableInfos)
            if len(updateColumnInfos) > 0:
                await self._column_info_mysql_repository.batch_update_column_infos(updateColumnInfos)
            else:
                await self._column_info_mysql_repository.batch_add_column_infos(columnInfos)
        # 返回所有字段的信息列表
        return columnInfos+updateColumnInfos

    async def build(self,file_path:str):
        '''
        :param file_path:  元数据配置文件的地址
        :return:
        '''
        # 注意：返回值为 None，本方法的产出全部体现在数据库里和这一次的 print 上
        # 加载配置文件
        meta_config : MetaConfig= load_config(file_path,MetaConfig)

        meta_mysql_client = CustomMySqlClient(appConfig.db_meta)   # 连元数据库
        dw_mysql_client = CustomMySqlClient(appConfig.db_dw)       # 连数据仓库

        meta_mysql_client.get_session_factory()   # 无返回值，靠副作用生成 sessionFactory
        dw_mysql_client.get_session_factory()
        # 同时打开两个会话：一个写元数据库、一个读数仓
        async  with meta_mysql_client.sessionFactory() as meta_session, dw_mysql_client.sessionFactory() as dw_session:
            self._column_info_mysql_repository =ColumnInfoMySqlRepository(meta_session)
            self._table_info_mysql_repository =TableInfoMySqlRepository(meta_session)
            self._dw_mysql_repostory = DwMysqlRepostory(dw_session)


            if meta_config is not None and meta_config.tables is not None:
                # 将tables数据解析并且写入到mysql数据库中
                columnInfos = await  self._save_tables_to_mysql(meta_config.tables)
                print('columnsInfo数据为：',columnInfos)
                # 注意：meta_config.metrics 读进来了但没有任何使用，指标表 t_metric_info 始终为空
