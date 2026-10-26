from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.agent_llm import llm
from app.agent.agent_runtime_context import AgentRuntimeContext
from app.agent.agent_state import AgentState, TableInfoState, ColumnInfoState, MetricInfoState
from app.entity.column_info_entity import ColumnInfoEntity
from app.entity.table_info_entity import TableInfoEntity
from app.entity.value_info import ValueInfo
from app.utils.loader_prompt_util import load_prompt_by_path


async  def mergeRetrieval(state:AgentState,runtime:Runtime[AgentRuntimeContext]):
    '''
        1、从状态中获取字段、指标、取值
        2、将指标中字段信息取出，查询mysql数据库
        3、取值的信息存入字段的examples属性中
        4、根据表的ID进行数据分组
        5、根据表id查询表的主键和外键
        6、构建完整的表信息和指标信息结构
    '''
    retrieval_columns = state["retrieval_columns"]
    retrieval_metrics = state["retrieval_metrics"]
    retrieval_values = state["retrieval_values"]

    # 从运行时上下文中获取对象
    column_mysql_repository = runtime.context['column_mysql_repository']
    table_mysql_repository = runtime.context['table_mysql_repository']
    # 将字段列表转换为字典，方便快速查询
    retrieval_columns_map = {
        retrieval_column.id: retrieval_column
        for retrieval_column in retrieval_columns
    }

    # 将指标信息的相关字段添加到字段字典中
    for metric in retrieval_metrics:
        relevant_columns  = metric.relevant_columns
        # 循环指标关联字段
        for retrieval_column in relevant_columns:
            # 判断指标字段id不在字段列表字典中，需要完善数据
            if retrieval_column not in retrieval_columns_map:
                column_info = await column_mysql_repository.get_column_info_by_id(retrieval_column)
                # 将查询的数据添加到字典中
                retrieval_columns_map[retrieval_column] = column_info

    #将取值合并到字段字典中
    for retrieval_value in retrieval_values:
        column_id = retrieval_value.column_id
        column_value = retrieval_value.value

        # 判断column_id是否在retrieval_columns_map，如果不在，则查询mysql数据
        if column_id not in retrieval_columns_map:
            column_info = await column_mysql_repository.get_column_info_by_id(column_id)
            retrieval_columns_map[retrieval_column] = column_info
        # 将取值添加examples字段
        retrieval_columns_map[retrieval_column].examples.append(column_value)

    # 按照字段所属的表ID进行分组
    table_to_columns_map :dict[str,list[ColumnInfoEntity]] = {}
    for column in retrieval_columns_map.values():
        table_id = column.table_id
        if table_id not in table_to_columns_map:
            table_to_columns_map[table_id] = []
        table_to_columns_map[table_id].append(column)

    for table_id in table_to_columns_map:
        # 查询表的主外键
        key_columns = await column_mysql_repository.get_key_by_table_id(table_id)
        #获取table_to_columns_map中指定表的所有的字段id
        column_ids = [column.id for column in table_to_columns_map[table_id]]
        # 循环主外键字段信息
        for key_column in key_columns:
            # 判断主外键字段id是否存在，不存在则添加
            if key_column.id not in column_ids:
                table_to_columns_map[table_id].append(key_column)

    # 将table_id -> columns映射转换为list[TableInfoState]
    table_infos: list[TableInfoState] = []
    for table_id,columns in table_to_columns_map.items():
        # 根据表id查询表的详细信息
        tableInfo:TableInfoEntity = await table_mysql_repository.get_table_info_by_id(table_id)

        columns_state = [
            ColumnInfoState(
                name=column.name,
                type=column.type,
                role=column.role,
                description=column.description,
                alias=column.alias,
                examples=column.examples,
            )
            for column in columns
        ]

        # 创建表信息的状态对象
        table_state = TableInfoState(
            name = tableInfo.name,
            role = tableInfo.role,
            description = tableInfo.description,
            columns=columns_state,
        )
        table_infos.append(table_state)

    metric_infos :list[MetricInfoState] = [
        MetricInfoState(
            name=metric.name,
            description=metric.description,
            retrieval_columns=metric.relevant_columns,
            alias=metric.alias,
        )
        for metric in retrieval_metrics
    ]
    writer = runtime.stream_writer
    writer({'table_infos':table_infos,'metric_infos':metric_infos})

    return {'table_infos':table_infos,'metric_infos':metric_infos}







