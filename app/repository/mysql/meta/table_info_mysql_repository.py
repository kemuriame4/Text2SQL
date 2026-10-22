from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.table_info_model import TableInfoModel


class TableInfoMysqlRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_table_info_by_id(self, table_info: TableInfoEntity):
        await self._session.add(TableInfoMapper.to_model(table_info))

    def batch_add_table_info(self, table_infos: list[TableInfoEntity]):
         self._session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])
    async def get_table_info_by_id(self, id: str):
        result = await self._session.get(TableInfoModel,id)
        if result:
            return TableInfoMapper.to_entity(result)
        return None
    async def update_table_info(self, table_info: TableInfoEntity):
        smt=  update(TableInfoModel).where(TableInfoModel.id==table_info.id).values(
            name=table_info.name,
            description=table_info.description,
            role=table_info.role,
        )
        await self._session.execute(smt)
    async def batch_update_table_infos(self, table_infos: list[TableInfoEntity]):
        smt= update(TableInfoModel)
        tables= [TableInfoMapper.to_model(table_info) for table_info in table_infos]
        await self._session.execute(smt, tables)
