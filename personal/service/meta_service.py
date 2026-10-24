from personal.config.meta_config import TableConfig
from personal.entity.column_entity import ColumnInfoEntity
from personal.entity.info_entity import TableInfoEntity


class MetaService:
    def __init__(self):
        pass

    async def _save_tables_to_mysql(self, tables: list[TableConfig]):
        async with self._table_info_mysql_repository.session.begin():
            table_infos = []
            update_table_infos = []
            column_infos = []
            update_column_infos = []
            for table in tables:
                table_info = TableInfoEntity(
                    id=table.name,
                    name=table.name,
                    description=table.description,
                    role=table.role,
                )

                row_table = (
                    await self._table_info_mysql_repository.get_table_info_by_id(
                        table_info.id
                    )
                )
                if row_table is not None:
                    update_table_infos.append(table_info)
                else:
                    table_infos.append(table_info)

                types = await self._dw_mysql_repository.get_column_type_by_name(
                    table.name
                )
                for column in table.columns:
                    examples = await self._dw_mysql_repository.get_column_values(
                        table.name, column.name
                    )

                    column_info = ColumnInfoEntity(
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        description=column.description,
                        role=column.role,
                        alias=column.alias,
                        type=types[column.name],
                        examples=examples,
                        table_id=table.name,
                    )

                    row_column = (
                        await self._column_info_mysql_repository.get_column_info_by_id(
                            column_info.id
                        )
                    )
                    if row_column is not None:
                        update_column_infos.append(column_info)
                    else:
                        column_infos.append(column_info)

                if len(update_table_infos) > 0:
                    await self._table_info_mysql_repository.batch_update_table_infos(
                        update_table_infos
                    )
                if len(table_infos) > 0:
                    await self._table_info_mysql_repository.batch_add_table_infos(
                        table_infos
                    )
                if len(update_column_infos) > 0:
                    await self._column_info_mysql_repository.batch_update_column_infos(
                        update_column_infos
                    )
                if len(column_infos) > 0:
                    await self._column_info_mysql_repository.batch_add_column_infos(
                        column_infos
                    )

            return column_infos + update_column_infos
