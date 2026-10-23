from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMysqlRepostory:
    def __init__(self,session:AsyncSession) :
        self.session = session

    async def get_column_type_by_name(self,table_name:str) :
        sql = f'show columns from {table_name}'
        result = await  self.session.execute(text(sql))
        # 将结果数据转换为字典
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self,table_name:str,column_name:str,limit: int = 5) :
        sql = f'select distinct {column_name} from {table_name} limit {limit} '
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()