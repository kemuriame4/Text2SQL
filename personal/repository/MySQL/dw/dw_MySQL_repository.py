from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_type_by_name(self, table_name: str):
        """
        获取表中字段的类型
        """
        SQL = f"show columns from {table_name}"

        result = await self.session.execute(text(SQL))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(
        self, table_name: str, column_name: str, limit: int = 5
    ):
        """
        获取字段的值
        """
        SQL = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(SQL))
        return result.scalars().fetchall()
