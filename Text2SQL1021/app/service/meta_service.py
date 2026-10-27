# 【文件作用】
# 这个文件是离线建库的“总调度”，负责把人工写好的元数据（表/字段/指标）分别写入 MySQL、Qdrant 向量库、Elasticsearch。
# 它是 app/script/meta_init.py 直接调用的对象；它自己不做具体读写，而是调用 repository 层（仓库管理员）去干活。
# 阅读建议：先看文件最后面的 build()（总流程），再回头看上面几个以 _ 开头的小方法。
import uuid   # uuid（通用唯一识别码）：用来给每条数据生成一个几乎不会重复的编号



# 下面这一批 import（导入）是把项目里其它文件已经写好的功能“借”过来用
from app.client.custom_embedding_client import CustomEmbeddingClient   # 向量化客户端（把一段文字变成一串数字，方便计算机比较两段话像不像）
from app.client.custom_es_client import CustomESClient   # ES 客户端（Elasticsearch：专门做全文搜索的数据库）
from app.client.custom_qdrant_client import CustomQdrantClient   # Qdrant 客户端（专门存放向量、做相似度搜索的数据库）
from app.client.mysql_client import CustomMySqlClient   # MySQL 客户端（连接关系型数据库的工具）
from app.conf.app_config import  appConfig   # 全局配置对象（数据库地址、账号密码等都从这里读）
from app.conf.meta_config import MetaConfig, TableConfig, MetricConfig   # 元数据的配置模板类（表、指标长什么样的“模具”）
from app.entity.column_info_entity import ColumnInfoEntity   # 字段信息实体类（一个字段包含哪些属性）
from app.entity.column_metric_entity import ColumnMetricEntity   # 字段-指标关联实体类（记录哪个字段属于哪个指标）
from app.entity.metric_info_entity import MetricInfoEntity   # 指标信息实体类（一个指标包含哪些属性）
from app.entity.table_info_entity import TableInfoEntity   # 表信息实体类（一张表包含哪些属性）
from app.entity.value_info import ValueInfo   # 字段取值实体类（记录某个字段有哪些具体值，供 ES 搜索用）
from app.repository.es.column_es_repository import ColumnEsRepository   # ES 仓库（负责往 ES 写字段取值）
from app.repository.mysql import column_info_mysql_repository   # 导入模块本身（下一行才是导入模块里的类）
from app.repository.mysql.column_info_mysql_repository import ColumnInfoMySqlRepository   # 字段表的 MySQL 仓库
from app.repository.mysql.column_metric_mysql_repository import ColumnMetricMySqlRepository   # 字段-指标关联表的 MySQL 仓库
from app.repository.mysql.dw import dw_mysql_repostory   # 导入模块本身（下一行才是导入模块里的类）
from app.repository.mysql.dw.dw_mysql_repostory import DwMysqlRepostory   # 数仓（dw = data warehouse 数据仓库）的 MySQL 仓库，用来查真实数据类型和具体取值
from app.repository.mysql.metric_info_mysql_repository import MetricInfoMySqlRepository   # 指标表的 MySQL 仓库
from app.repository.mysql.table_info_mysql_repository import TableInfoMySqlRepository   # 表信息表的 MySQL 仓库
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository   # 字段向量库仓库
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository   # 指标向量库仓库
from app.utils.load_config_util import load_config   # 配置加载工具（把外层的 yaml 配置和内层的模板类合并、校验，得到配置对象）


class MetaService:   # 定义服务类 MetaService（服务层：负责编排流程，具体的读写交给仓库层）
    def __init__(self):   # 构造函数（创建对象时会自动执行一次）
        pass   # 什么都不做：这个类不需要提前初始化属性，属性都在 build() 里现场赋值

    async def _save_tables_to_mysql(self, tables: list[TableConfig]):   # 异步方法（发出去不用干等结果，可以先干别的）：把表信息和字段信息整理好、准备写进元数据库
        # 方法名以 _ 开头表示“内部方法”，只给本文件自己用
        # 开启会话
        async  with self._table_info_mysql_repository.session.begin():   # 开启一个数据库事务（一批操作要么全部成功，要么全部回滚）
            # 将TableConfig转换为TableInfoEntity和ColumnInfoEntity
            tableInfos = []   # 待新增的表信息列表
            updateTableInfos = []   # 待更新的表信息列表（数据库里已经存在的）
            columnInfos = []   # 待新增的字段信息列表
            updateColumnInfos = []   # 待更新的字段信息列表（数据库里已经存在的）
            # 循环表信息
            for table in tables:   # 一张表一张表地处理
                # 构建表信息
                tableInfo = TableInfoEntity(   # 把配置里的“表”包装成实体对象
                    id= table.name,   # 用表名当主键 id
                    name= table.name,   # 表名
                    description= table.description,   # 表的中文说明（给大模型看的）
                    role= table.role,   # 表的角色（比如事实表/维度表）
                )
                # 将数据添加到列表中
                # 查询数据是否存在
                rowTable = await self._table_info_mysql_repository.get_table_info_by_id(tableInfo.id)   # 去元数据库查这张表是否已存在
                if rowTable is not None:   # 查到了说明是旧数据
                    updateTableInfos.append(tableInfo)   # 放进“待更新”队列
                else:   # 没查到说明是新表
                    tableInfos.append(tableInfo)   # 放进“待新增”队列
                # tableInfos.append(tableInfo)
                # type 从数据仓库中获取字段的数据类型
                types =await self._dw_mysql_repostory.get_column_type_by_name(table.name)   # 去数仓查这张表所有字段的真实数据类型，返回一个字典
                # 【注意】上面按表逐张查数仓，下面按字段逐个查数仓，属于 N+1 查询问题（循环里一条条查库，交互次数多、慢），数据量大时会明显变慢

                for column in table.columns:   # 逐个处理这张表下的字段
                    # examples 从数据仓库中获取数据
                    examples = await  self._dw_mysql_repostory.get_column_values(table.name,column.name)   # 去数仓捞这个字段的一些真实取值，作为示例
                    # 【注意】这一行在 for 循环内部，每处理一个字段就查一次库，同样是 N+1 问题
                    # 构建字段的对象数据
                    columnInfo = ColumnInfoEntity(   # 把配置里的“字段”包装成实体对象
                        id = f'{table.name}.{column.name}',   # 主键 id 用“表名.字段名”拼出来，保证全局唯一
                        name= column.name,   # 字段名
                        description= column.description,   # 字段的中文说明（给大模型看的）
                        role= column.role,   # 字段角色（比如维度/度量）
                        alias= column.alias,   # 字段别名/同义词列表（用户可能用别的说法提问）
                        # 从字典中获取数据类型
                        type=types[column.name],   # 从前面查到的类型字典里取出这个字段的类型
                        # 【注意】如果数仓里没有这个字段，字典里取不到，这里会抛 KeyError，建议取值前先判断键是否存在
                        examples=examples,   # 上面从数仓捞到的示例值
                        table_id= table.name,   # 所属表的表名
                        # qdrant_id= uuid.uuid4(),   # 原有注释保留：向量库里那条数据的 id，这里先不用
                    )
                    # 判断字段是否存在
                    rowColumn = await self._column_info_mysql_repository.get_column_info_by_id(columnInfo.id)   # 去元数据库查这个字段是否已存在
                    if rowColumn is not None:   # 查到了说明旧数据
                        # columnInfo.qdrant_id = rowColumn.qdrant_id   # 原有注释保留：想沿用旧的向量 id
                        updateColumnInfos.append(columnInfo)   # 放进“待更新”队列
                    else:   # 没查到说明是新字段
                        columnInfos.append(columnInfo)   # 放进“待新增”队列

            #  校验是否存在，
            # 【注意】下面 4 组代码整段被注释掉了，等于这个方法虽然查了库、分好了新增/更新队列，但一条都没真正写进 MySQL
            # 【注意】这也是为什么 build() 只能拿到整理好的字段列表去写 ES，元数据库里实际上不会多出表/字段数据
            # if len(updateTableInfos) > 0:
            #     await self._table_info_mysql_repository.batch_update_table_infos(updateTableInfos)
            # if len(tableInfos) > 0:
            #     await  self._table_info_mysql_repository.batch_add_table_infos(tableInfos)
            # if len(updateColumnInfos) > 0:
            #     await self._column_info_mysql_repository.batch_update_column_infos(updateColumnInfos)
            # if len(columnInfos) > 0:
            #     await self._column_info_mysql_repository.batch_add_column_infos(columnInfos)
        # 返回所有字段的信息列表
        return columnInfos+updateColumnInfos   # 把新增和更新的字段合并成一个列表返回（+ 号是列表拼接）

    async def _save_columns_to_qdrant(self,column_infos:list[ColumnInfoEntity]):   # 异步方法：把字段信息向量化后写进 Qdrant 向量库
        # 创建集合
        await self._column_qdrant_repository.create_collection()   # create_collection（在向量库里建一张“表”，向量库叫它集合 collection）
        points: list[dict] = []   # 准备要插入的“点”（向量库里的一条记录叫 point）
        i = 0   # 计数器，用来给同名字段的不同文本编序号
        # 【注意】循环外这行 i = 0 其实没用，因为循环体内第一行又把它重置成 0 了
        for columnInfo in column_infos:   # 逐个字段处理
            i = 0   # 每个字段重新从 0 开始计数
            points.append({   # 第 0 条：用字段名做向量文本
                'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{columnInfo.table_id}_{columnInfo.name}_{i}'),   # uuid5：根据“字符串”算出固定不变的 id（同样的字符串永远得出同样的 id）
                'embedding_text': columnInfo.name,   # 待向量化的文本（字段名）
                'payload': columnInfo   # payload（随向量一起存的原始数据，方便搜索后取回）
            })
            i += 1   # 序号加一
            points.append({   # 第 1 条：用字段说明做向量文本
                'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{columnInfo.table_id}_{columnInfo.name}_{i}'),   # 同样方式生成不会重复的 id
                'embedding_text': columnInfo.description,   # 待向量化的文本（字段说明）
                'payload': columnInfo   # 一起存原始数据
            })

            for alias in columnInfo.alias:   # 每个别名也各存一条，方便用户用同义词搜到
                i += 1   # 序号继续加一
                points.append({   # 第 2、3… 条：用别名做向量文本
                    'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{columnInfo.table_id}_{columnInfo.name}_{i}'),   # 生成不重复的 id
                    'embedding_text': alias,   # 待向量化的文本（别名）
                    'payload': columnInfo   # 一起存原始数据
                })

        embedding_texts = [point['embedding_text'] for point in points]   # 把所有待向量化的文本抽出来成一个列表（列表推导式）
        ids = [point['id'] for point in points]   # 把所有 id 抽出来
        payloads = [point['payload'] for point in points]   # 把所有原始数据抽出来
        embeddings = []   # 装向量结果的空列表
        # 将embedding_text 向量化
        batch_embedding = 20   # 每批处理 20 条，避免一次请求太大、被服务限流
        for i in range(0,len(embedding_texts),batch_embedding):   # 从头到尾按 20 条一批切片
            # 【注意】这里的 i 复用了外层计数器的变量名，覆盖了上面的 i，容易看晕（不影响结果）
            batch_embedding_texts = embedding_texts[i:i+batch_embedding]   # 切出当前这一批文本
            batch_embeddings = await self._embedding_client.aembed_documents(batch_embedding_texts)   # 调向量化服务，把这一批文本变成数字向量
            embeddings.extend(batch_embeddings)   # 把这一批向量拼到总结果里
        await self._column_qdrant_repository.insert_and_update(ids,embeddings,payloads)   # 把 id、向量、原始数据一起写进向量库（有则更新、无则插入）

    async def _save_metrics_to_qdrant(self,metric_infos:list[MetricInfoEntity]):   # 异步方法：把指标信息向量化后写进 Qdrant（逻辑和字段那份几乎一样）
        # 创建集合
        await self._metric_qdrant_repository.create_collection()   # 在向量库里建指标的集合
        points: list[dict] = []   # 要插入的点
        i = 0   # 计数器
        for metricInfo in metric_infos:   # 逐个指标处理
            i = 0   # 每个指标重新从 0 开始计数
            points.append({   # 第 0 条：用指标名做向量文本
                'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{metricInfo.name}_{i}'),   # 由指标名和序号生成固定 id
                'embedding_text': metricInfo.name,   # 待向量化文本（指标名）
                'payload': metricInfo   # 原始数据
            })
            i += 1   # 序号加一
            points.append({   # 第 1 条：用指标说明做向量文本
                'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{metricInfo.name}_{i}'),   # 生成 id
                'embedding_text': metricInfo.description,   # 待向量化文本（指标说明）
                'payload': metricInfo   # 原始数据
            })

            for alias in metricInfo.alias:   # 每个别名也存一条
                i += 1   # 序号加一
                points.append({   # 别名那条
                    'id': uuid.uuid5(uuid.NAMESPACE_DNS,f'{metricInfo.name}_{i}'),   # 生成 id
                    'embedding_text': alias,   # 待向量化文本（别名）
                    'payload': metricInfo   # 原始数据
                })

        embedding_texts = [point['embedding_text'] for point in points]   # 抽出所有待向量化文本
        ids = [point['id'] for point in points]   # 抽出所有 id
        payloads = [point['payload'] for point in points]   # 抽出所有原始数据
        embeddings = []   # 装向量结果
        # 将embedding_text 向量化
        batch_embedding = 20   # 每批 20 条
        for i in range(0,len(embedding_texts),batch_embedding):   # 按批遍历
            batch_embedding_texts = embedding_texts[i:i+batch_embedding]   # 切出当前批
            batch_embeddings = await self._embedding_client.aembed_documents(batch_embedding_texts)   # 调向量化服务转成向量
            embeddings.extend(batch_embeddings)   # 拼到总结果
        await self._metric_qdrant_repository.insert_and_update(ids,embeddings,payloads)   # 写进向量库

    async  def _save_columns_to_es(self,column_infos:list[ColumnInfoEntity], tables:TableConfig):   # 异步方法：把字段的“具体取值”写进 ES，方便用户说的具体值也能被搜到
        # 【注意】第二个参数类型写的是 TableConfig，但 build() 传进来的是“表配置的列表”，注解和实际不符（不影响运行）
        # 将tables下的所有的column信息转换为dict
        column2sync :dict[str,bool] = {}   # 建一个字典：键是“表名.字段名”，值是“这个字段要不要同步到 ES”
        for table in tables:   # 遍历每张表
            for column in table.columns:   # 遍历表里的每个字段
                column2sync[f'{table.name}.{column.name}'] = column.sync   # 把配置里的 sync 开关记下来

        valueInfos:list[ValueInfo] = []   # 装所有“字段取值”对象
        for columnInfo in column_infos:   # 遍历每个字段信息
            sync = column2sync.get(columnInfo.id,False)   # 查这个字段的同步开关；字典里没有就默认 False（不同步）

            if sync:   # 只有开关为真才处理
                table_name = columnInfo.table_id   # 取出表名
                column_name = columnInfo.name   # 取出字段名
                values = await self._dw_mysql_repostory.get_column_values(table_name,column_name,10000)   # 去数仓取这个字段的最多 10000 个不同的值

                current_value_infos = [   # 列表推导式：每个取值生成一个 ValueInfo 对象
                    ValueInfo(   # 构造字段取值对象
                        id= f'{columnInfo.id}.{value}',   # id = 字段id + 取值，保证唯一
                        value= values,   # 【注意】这里疑似笔误：写成了 values（整个列表），本意应是 value=value（当前这一个值）
                        # 【注意】后果是每条记录的 value 都存成了整个列表，ES 里的取值数据会是错的
                        column_id=columnInfo.id   # 属于哪个字段
                    ) for value in values   # 对每个取值循环一次
                ]   # 列表推导式结束
                valueInfos.extend(current_value_infos)   # 把这一批追加到总列表
        # 将数据写入到es中
        # 创建es的索引
        await self._column_es_repository.createIndex()   # index（ES 里相当于“表”，中文常叫索引）
        # 写入数据
        await self._column_es_repository.insertIndex(valueInfos)   # 批量写入这些取值数据



    async  def _save_metrics_to_mysql(self,metrics:list[MetricConfig]):   # 异步方法：把指标信息整理成实体对象，准备写 MySQL
        # 循环对象组装数据
        metric_infos:list[MetricInfoEntity] = []   # 装指标实体
        column_metrics: list[ColumnMetricEntity] = []   # 装“字段-指标”关联实体

        for metric in metrics:   # 逐个指标处理
            metric_info = MetricInfoEntity(   # 把配置里的指标包装成实体
                id= metric.name,   # 用指标名当主键
                name=metric.name,   # 指标名
                description=metric.description,   # 指标说明（给大模型看的）
                alias= metric.alias,   # 指标别名/同义词
                relevant_columns= metric.relevant_columns,   # 这个指标涉及哪些字段
            )

            metric_infos.append(metric_info)   # 加进指标列表

            for column in metric.relevant_columns:   # 遍历这个指标涉及的每个字段
                column_metrics.append(ColumnMetricEntity(   # 建一条“字段↔指标”的关联记录
                    column_id=column,   # 字段 id
                    metric_id=metric.name,   # 指标 id
                ))


        print(metric_infos)   # 【注意】调试用的打印没删，会把指标数据打到控制台
        print("==============")   # 打印一条分隔线
        print(column_metrics)   # 打印关联数据（同样是调试残留）

        # 将数据写入到数据库中
        # 【注意】下面两行写库代码被注释掉了，所以指标数据其实并没有写进 MySQL，只是组装好返回了
        # async with self._metric_info_mysql_repository.session.begin():
        #     await  self._metric_info_mysql_repository.batch_insert_data(metric_infos)
        #     await  self._column_metric_mysql_repository.batch_insert_data(column_metrics)
        # 返回指标信息
        return metric_infos   # 返回指标列表（供后面写向量库用）


    async def build(self,file_path:str):   # 总调度方法（异步）：整个离线建库流程都从这里开始
        # 下面这个三引号是文档注释（用来说明函数参数），不是可执行代码
        '''
        :param file_path:  元数据配置文件的地址
        :return:
        '''
        # 加载配置文件
        meta_config : MetaConfig= load_config(file_path,MetaConfig)   # 读取 yaml 配置，合并、校验后得到 MetaConfig 对象

        meta_mysql_client = CustomMySqlClient(appConfig.db_meta)   # 建“元数据库”（meta 库）的连接客户端
        dw_mysql_client = CustomMySqlClient(appConfig.db_dw)   # 建“数仓”（dw 库）的连接客户端（同一个 MySQL 实例，只是库名不同）

        meta_mysql_client.get_session_factory()   # 初始化元数据库的会话工厂（批量生产数据库会话的工厂）
        dw_mysql_client.get_session_factory()   # 初始化数仓的会话工厂

        # 获取qdrant连接
        qdrant_client = CustomQdrantClient(appConfig.qdrant)   # 建向量库客户端
        qdrant_client.get_client()   # 真正建立连接

        self._embedding_client = CustomEmbeddingClient(appConfig.embedding).get_client()   # 建向量化服务的客户端，存成对象属性供后面用

        # es的客户端
        self._es_client = CustomESClient(appConfig.es).get_client()   # 建 ES 客户端
        # 实例化数据交互层ColumnQdrantRepository
        async  with meta_mysql_client.sessionFactory() as meta_session, dw_mysql_client.sessionFactory() as dw_session:   # 同时开两个数据库会话（一个连 meta 库、一个连 dw 库），用完自动关闭
            self._column_info_mysql_repository =ColumnInfoMySqlRepository(meta_session)   # 字段表的仓库
            self._table_info_mysql_repository =TableInfoMySqlRepository(meta_session)   # 表信息表的仓库
            self._column_metric_mysql_repository =ColumnMetricMySqlRepository(meta_session)   # 字段-指标关联表的仓库
            self._metric_info_mysql_repository =MetricInfoMySqlRepository(meta_session)   # 指标表的仓库

            self._dw_mysql_repostory = DwMysqlRepostory(dw_session)   # 数仓仓库（查真实数据类型和取值）
            self._column_qdrant_repository = ColumnQdrantRepository(qdrant_client.client,appConfig.embedding.embedding_size)   # 字段向量仓库（带上向量维度大小）
            self._metric_qdrant_repository = MetricQdrantRepository(qdrant_client.client,appConfig.embedding.embedding_size)   # 指标向量仓库
            self._column_es_repository = ColumnEsRepository(self._es_client)   # 字段取值 ES 仓库
            if meta_config is not None and meta_config.tables is not None:   # 配置存在、并且配置了表，才处理表
                # 将tables数据解析并且写入到mysql数据库中
                columnInfos = await  self._save_tables_to_mysql(meta_config.tables)   # 整理表/字段信息（注意：由于写库代码被注释，这一步实际只返回列表，没写库）
                # print('columnsInfo数据为：',columnInfos)
                # 将字段信息写入到qdrant
                # await  self._save_columns_to_qdrant(columnInfos)   # 【注意】这行被注释掉，字段向量没有真正写进向量库
            #     # 将字段信息写入es中
                await  self._save_columns_to_es(columnInfos,meta_config.tables)   # 把字段的具体取值写进 ES

            # 指标信息写入到 mysql 、 qdrant
            if meta_config is not None and meta_config.metrics is not None:   # 配置存在、并且配置了指标，才处理指标
                metric_infos = await  self._save_metrics_to_mysql(meta_config.metrics)   # 整理指标信息（同样没真正写 MySQL）
                await  self._save_metrics_to_qdrant(metric_infos)   # 把指标信息向量化后写进向量库
