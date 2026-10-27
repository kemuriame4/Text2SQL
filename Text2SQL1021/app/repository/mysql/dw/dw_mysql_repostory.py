# 【文件作用】
# 这个文件负责读写数仓 dw 库（真正存业务数据的地方，比如 fact_order 订单事实表和 4 张维度表）。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 它主要干两件事：查某张表里每个字段是什么类型；查某个字段的前几个不同取值（用来补全 SQL 条件）。
# 【注意】文件名 DwMysqlRepostory 里的 Repostory 少了一个 i，正确拼写是 Repository（历史拼写错误，代码里没改名）。

from sqlalchemy import text  # 导入 text：用来直接执行手写的原生 SQL 字符串
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步会话类型（会话 session = 和数据库之间的一条连接通道）


class DwMysqlRepostory:  # 定义"数仓 MySQL 仓库"类
    def __init__(self,session:AsyncSession) :  # 构造方法：创建对象时传入一个数据库会话
        self.session = session  # 把会话存进对象里，后面每个方法都能拿来用

    async def get_column_type_by_name(self,table_name:str) :  # 按表名查出这张表"字段名 -> 字段类型"的对应关系
        # 【注意】表名是直接用 f-string 拼进 SQL 的，只适合传入内部可信的表名（不能直接接用户输入）
        sql = f'show columns from {table_name}'  # 拼出 MySQL 的 SHOW COLUMNS 语句：列出这张表的所有字段
        result = await  self.session.execute(text(sql))  # 执行这条 SQL，拿到结果集
        # 将结果数据转换为字典
        return {row.Field: row.Type for row in result.fetchall()}  # 每行取 Field（字段名）当键、Type（字段类型）当值，拼成字典返回
        # 【注意】SHOW COLUMNS 其实还会返回 Comment（字段的中文注释）这一列，但这里只取了 Field 和 Type，中文注释被丢掉了

    async def get_column_values(self,table_name:str,column_name:str,limit: int = 5) :  # 查某个字段的前 limit 个不同取值
        sql = f'select distinct {column_name} from {table_name} limit {limit} '  # DISTINCT 去重只留不同取值；limit 控制最多取几条
        result = await self.session.execute(text(sql))  # 执行这条 SQL，拿到结果集
        return result.scalars().fetchall()  # scalars() 只取第一列（也就是字段值本身），fetchall() 把全部行取出来