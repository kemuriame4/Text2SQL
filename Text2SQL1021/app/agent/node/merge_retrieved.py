# 【文件作用】
# 这是图里的第 5 个节点（工位），负责"结果合并"：把前面三路检索回来的字段、指标、取值汇成一份完整资料。
# 它从 state 里读 retrieval_columns / retrieval_metrics / retrieval_values，
# 去 MySQL 补全字段和表的完整信息，最后返回 {'table_infos': [...], 'metric_infos': [...]}。
from langchain_core.output_parsers import JsonOutputParser  # 【注意】导入了但本文件没用到（多余的 import）
from langchain_core.prompts import PromptTemplate  # 【注意】导入了但本文件没用到
from langgraph.runtime import Runtime  # 导入 Runtime 类型，只用来标注参数类型

from app.agent.agent_llm import llm  # 【注意】导入了但本文件没用到
from app.agent.agent_runtime_context import AgentRuntimeContext  # 导入运行时上下文的类型
from app.agent.agent_state import AgentState, TableInfoState, ColumnInfoState, MetricInfoState  # 导入全局状态和几种输出结构的类型
from app.entity.column_info_entity import ColumnInfoEntity  # 导入字段实体类（只用于类型标注）
from app.entity.table_info_entity import TableInfoEntity  # 导入表实体类（只用于类型标注）
from app.entity.value_info import ValueInfo  # 【注意】导入了但本文件没用到
from app.utils.loader_prompt_util import load_prompt_by_path  # 【注意】导入了但本文件没用到


# 【作用】定义"结果合并"节点函数：把三路检索结果合成完整的表、字段、指标资料。
async  def mergeRetrieval(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    # 【函数说明】这个节点的 6 个步骤写在下面三引号字符串里，只是给人看的说明，程序不会执行它。
    '''
        1、从状态中获取字段、指标、取值
        2、将指标中字段信息取出，查询mysql数据库
        3、取值的信息存入字段的examples属性中
        4、根据表的ID进行数据分组
        5、根据表id查询表的主键和外键
        6、构建完整的表信息和指标信息结构
    '''
    retrieval_columns = state["retrieval_columns"]  # 取出字段召回节点找到的字段列表
    retrieval_metrics = state["retrieval_metrics"]  # 取出指标召回节点找到的指标列表
    retrieval_values = state["retrieval_values"]  # 取出取值召回节点找到的字段取值列表

    # 从运行时上下文中获取对象
    column_mysql_repository = runtime.context['column_mysql_repository']  # 取出"字段表"的 MySQL 查询对象
    table_mysql_repository = runtime.context['table_mysql_repository']  # 取出"表信息"的 MySQL 查询对象
    # 将字段列表转换为字典，方便快速查询
    retrieval_columns_map = {  # 构造"字段id → 字段对象"的字典（像通讯录，用 id 当钥匙快速找到字段）
        retrieval_column.id: retrieval_column  # 键=字段 id，值=字段对象
        for retrieval_column in retrieval_columns  # 遍历所有召回的字段（这种一行写完循环的写法叫字典推导式）
    }

    # 将指标信息的相关字段添加到字段字典中
    for metric in retrieval_metrics:  # 遍历每个召回的指标
        relevant_columns  = metric.relevant_columns  # 取出这个指标关联的字段 id 列表
        # 循环指标关联字段
        for retrieval_column in relevant_columns:  # 【注意】变量名虽然叫 retrieval_column，但这里其实是一个字段 id 字符串，容易误解
            # 判断指标字段id不在字段列表字典中，需要完善数据
            if retrieval_column not in retrieval_columns_map:  # 如果这个字段 id 还没在字典里
                column_info = await column_mysql_repository.get_column_info_by_id(retrieval_column)  # 就去 MySQL 查这个字段的完整信息
                # 将查询的数据添加到字典中
                retrieval_columns_map[retrieval_column] = column_info  # 用字段 id 当键存进字典

    #将取值合并到字段字典中
    for retrieval_value in retrieval_values:  # 遍历每个召回的取值
        column_id = retrieval_value.column_id  # 取出这个取值属于哪个字段（字段 id）
        column_value = retrieval_value.value  # 取出取值本身（比如"华东""在职"）

        # 判断column_id是否在retrieval_columns_map，如果不在，则查询mysql数据
        if column_id not in retrieval_columns_map:  # 如果这个字段还没被召回
            column_info = await column_mysql_repository.get_column_info_by_id(column_id)  # 就去 MySQL 补查这个字段的信息
            retrieval_columns_map[column_id] = column_info  # 存进字典
        # 将取值添加examples字段
        # 【注意】examples 可能是 None（数据库里没存示例值），直接 .append 会报 AttributeError。
        # 【注意】同一个取值重复命中时会被重复追加，这里没有去重。
        retrieval_columns_map[column_id].examples.append(column_value)  # 把这个取值塞进字段的"示例值"列表里

    # 按照字段所属的表ID进行分组
    table_to_columns_map :dict[str,list[ColumnInfoEntity]] = {}  # 准备"表id → 该表所有字段列表"的空字典
    for column in retrieval_columns_map.values():  # 只遍历字典的值（也就是一个个字段对象）
        table_id = column.table_id  # 取出这个字段属于哪张表
        if table_id not in table_to_columns_map:  # 如果这张表还没建过分组
            table_to_columns_map[table_id] = []  # 就先放一个空列表占位
        table_to_columns_map[table_id].append(column)  # 把字段追加到它所属表的分组里

    for table_id in table_to_columns_map:  # 逐个表处理（遍历字典默认拿到的是键，也就是 table_id）
        # 查询表的主外键
        key_columns = await column_mysql_repository.get_key_by_table_id(table_id)  # 查这张表的主键、外键字段（SQL 里固定只查这两类）
        #获取table_to_columns_map中指定表的所有的字段id
        column_ids = [column.id for column in table_to_columns_map[table_id]]  # 把这张表现有的字段 id 收集成列表，方便判断是否重复
        # 循环主外键字段信息
        for key_column in key_columns:  # 遍历查回来的每个主键/外键字段
            # 判断主外键字段id是否存在，不存在则添加
            if key_column.id not in column_ids:  # 如果这个主外键字段还没在这张表的列表里
                table_to_columns_map[table_id].append(key_column)  # 就补进去（后面生成 SQL 连接多张表时要用到主外键）

    # 将table_id -> columns映射转换为list[TableInfoState]
    table_infos: list[TableInfoState] = []  # 准备最终要返回的"表信息"列表
    for table_id,columns in table_to_columns_map.items():  # 同时拿到表 id 和该表的字段列表（items() 一次给键和值）
        # 根据表id查询表的详细信息
        tableInfo:TableInfoEntity = await table_mysql_repository.get_table_info_by_id(table_id)  # 去 MySQL 查这张表的名称、角色、描述

        # 【说明】下面用"列表推导式"把每个字段对象转换成只含必要信息的状态对象。
        columns_state = [
            ColumnInfoState(  # 构造一个字段状态对象
                name=column.name,  # 字段名
                type=column.type,  # 字段类型（比如 varchar、int）
                role=column.role,  # 字段角色（普通字段 / 主键 / 外键）
                description=column.description,  # 字段的业务描述
                alias=column.alias,  # 字段别名列表（用户可能用别的叫法）
                examples=column.examples,  # 字段的示例取值
            )
            for column in columns  # 遍历这张表的所有字段
        ]

        # 创建表信息的状态对象
        table_state = TableInfoState(  # 构造这张表的状态对象
            name = tableInfo.name,  # 表名
            role = tableInfo.role,  # 表角色（事实表 / 维度表）
            description = tableInfo.description,  # 表描述
            columns=columns_state,  # 上面整理好的字段列表
        )
        table_infos.append(table_state)  # 把这张表加进最终的表列表

    # 【说明】把每个指标对象转换成只含必要信息的状态对象。
    metric_infos :list[MetricInfoState] = [
        MetricInfoState(  # 构造一个指标状态对象
            name=metric.name,  # 指标名（比如"销售额"）
            description=metric.description,  # 指标说明
            retrieval_columns=metric.relevant_columns,  # 这个指标依赖的字段 id 列表
            alias=metric.alias,  # 指标别名列表（用户可能说的同义词）
        )
        for metric in retrieval_metrics  # 遍历所有召回的指标
    ]
    writer = runtime.stream_writer  # 拿到流式输出的写入口
    writer({'table_infos':table_infos,'metric_infos':metric_infos})  # 把最终汇总结果实时推给前端

    return {'table_infos':table_infos,'metric_infos':metric_infos}  # 只返回本节点更新的两个字段，交给下游生成 SQL 的节点







