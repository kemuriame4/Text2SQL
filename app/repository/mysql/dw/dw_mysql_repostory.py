"""数据仓库访问层：只读数据仓库（dw 库），给元数据补上"真实数据类型"和"示例取值"。"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMysqlRepostory:
    """只负责从数据仓库读两类信息，不做任何写入。"""

    def __init__(self,session:AsyncSession) :
        """
        做什么：注入一个连到数据仓库的异步会话。
        参数：
        session (AsyncSession)：必须是连 dw 库的会话，不能是元数据库的会话。
        返回：
        无。
        """
        self.session = session

    async def get_column_type_by_name(self,table_name:str) :
        """
        做什么：执行 SHOW COLUMNS，拿到这张表所有字段的真实类型。
        参数：
        table_name (str)：数据仓库里的表名，如 dim_region。
        返回：
        dict[str, str]：字段名 → 类型，如 {'region_id': 'bigint', 'region_name': 'varchar(64)'}。
        注意：① 表不存在时驱动会抛 OperationalError（MySQL 1146），这里没有捕获；
              ② 表名是 f-string 直接拼进 SQL 的，没有做校验；
              ③ 返回的就是 MySQL 原始类型串，不会归一化成通用的 varchar/int。
        """
        sql = f'show columns from {table_name}'      # 表名是拼进去的，无参数化
        result = await  self.session.execute(text(sql))
        # 将结果数据转换为字典
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self,table_name:str,column_name:str,limit: int = 5) :
        """
        做什么：取某一列的"去重后"的若干个取值，作为该字段的示例数据（examples）。
        参数：
        table_name (str)：数据仓库里的表名，如 dim_region。
        column_name (str)：列名，如 region_name。
        limit (int)：最多取多少个不同的值，默认 5；可填。
        返回：
        list：去重后的取值列表，长度 0 ~ limit，类型由数据库驱动决定。
        None 值也会作为其中一个取值返回，没有过滤掉。
        注意：① 用 distinct 是为了拿"值域"而不是"前 5 行"；
              ② 结果里可能有 Decimal / date 这类非 JSON 原生类型，写 JSON 列前要处理；
              ③ 表名、列名都是拼进 SQL 的，没有做校验；
              ④ 没有 order by，每次抽出的示例值顺序不保证稳定。
        """
        sql = f'select distinct {column_name} from {table_name} limit {limit} '   # 取去重值域
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()
