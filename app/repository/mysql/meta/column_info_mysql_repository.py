from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMysqlRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_column_info(self, column_info: ColumnInfoEntity):
        # session.add 是同步方法，切勿 await
        self._session.add(ColumnInfoMapper.to_model(column_info))

    async def batch_add_column_info(self, column_infos: list[ColumnInfoEntity]):
        self._session.add_all([ColumnInfoMapper.to_model(t) for t in column_infos])

    async def get_column_info_by_id(self, id: str) -> ColumnInfoEntity | None:
        result = await self._session.get(ColumnInfoModel, id)
        if result:
            return ColumnInfoMapper.to_entity(result)
        return None

    async def update_column_info(self, column_info: ColumnInfoEntity):
        stmt = (
            update(ColumnInfoModel)
            .where(ColumnInfoModel.id == column_info.id)
            .values(
                name=column_info.name,
                role=column_info.role,
                description=column_info.description,
                update_time=column_info.update_time,
                update_by=column_info.update_by,
            )
        )
        await self._session.execute(stmt)

    async def batch_update_column_infos(self, column_infos: list[ColumnInfoEntity]):
        """批量更新：ORM 按主键逐行 UPDATE（参数字典必须包含真实主键列名 id）。"""
        if not column_infos:
            return
        stmt = update(ColumnInfoModel).execution_options(synchronize_session=None)
        params = [
            {
                'id': t.id,
                'name': t.name,
                'type': t.type,
                'role': t.role,
                'examples': t.examples,
                'description': t.description,
                'alias': t.alias,
                'update_time': t.update_time,
                'update_by': t.update_by,
            }
            for t in column_infos
        ]
        await self._session.execute(stmt, params)
