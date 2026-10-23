from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.table_info_model import TableInfoModel


class TableInfoMysqlRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_table_info(self, table_info: TableInfoEntity):
        # session.add 是同步方法，切勿 await
        self._session.add(TableInfoMapper.to_model(table_info))

    async def batch_add_table_info(self, table_infos: list[TableInfoEntity]):
        self._session.add_all([TableInfoMapper.to_model(t) for t in table_infos])

    async def get_table_info_by_id(self, id: str) -> TableInfoEntity | None:
        result = await self._session.get(TableInfoModel, id)
        if result:
            return TableInfoMapper.to_entity(result)
        return None

    async def update_table_info(self, table_info: TableInfoEntity):
        stmt = (
            update(TableInfoModel)
            .where(TableInfoModel.id == table_info.id)
            .values(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                update_time=table_info.update_time,
                update_by=table_info.update_by,
            )
        )
        await self._session.execute(stmt)

    async def batch_update_table_infos(self, table_infos: list[TableInfoEntity]):
        """批量更新：ORM 按主键逐行 UPDATE（参数字典必须包含真实主键列名 id）。"""
        if not table_infos:
            return
        stmt = update(TableInfoModel).execution_options(synchronize_session=None)
        params = [
            {
                'id': t.id,
                'name': t.name,
                'role': t.role,
                'description': t.description,
                'update_time': t.update_time,
                'update_by': t.update_by,
            }
            for t in table_infos
        ]
        await self._session.execute(stmt, params)
