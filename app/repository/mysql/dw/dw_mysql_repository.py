import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_IDENTIFIER_RE = re.compile(r'^[A-Za-z0-9_]+$')


def _validate_identifier(name: str, field: str) -> str:
    """标识符白名单校验，防止表名/列名注入。"""
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f'非法的 SQL 标识符 {field}: {name!r}')
    return name


class DwMysqlRepository:
    """dw 库只读查询：反查列类型与示例数据。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_type_by_name(self, table_name: str) -> dict[str, str]:
        """desc 反查 dw 表各列数据类型，返回 {列名: 类型}。"""
        _validate_identifier(table_name, 'table_name')
        sql = f'desc {table_name}'
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_examples_by_name(self, table_name: str, column_name: str, limit: int) -> list:
        """按列去重抽取示例数据，返回标量值列表。"""
        _validate_identifier(table_name, 'table_name')
        _validate_identifier(column_name, 'column_name')
        sql = f'select distinct {column_name} from {table_name} limit {int(limit)}'
        result = await self.session.execute(text(sql))
        return list(result.scalars().fetchall())
