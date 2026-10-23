from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
class DwMysqlRepostory:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def get_column_type_by_name(self,name:str):
        sql = f"desc {name}"
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self,table_name:str,column:str,limit:int = 5):
        sql = f"select distinct {column} from {table_name} limit {limit}"
        result =  await self.session.execute(text(sql))
        return result.scalar().fetchall()

