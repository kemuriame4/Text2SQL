from app.conf.meta_config import TableConfig


class MetaService:
    def __init__(self):
        pass

    async def _save_tables_to_mysql(self,tables:list[TableConfig]):
        # 开启会话
        async with self._table_info_mysql_repository.session.begin():
