from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.table_info_model import TableInfoModel


class TableInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        #设置为私有的session会话
        self._session = session

    async def get_table_info_by_id(self,id:str):
        result :TableInfoModel = await  self._session.get(TableInfoModel,id)
        if result is None:
            return None
        return TableInfoMapper.to_entity(result)

    async def add_table_info(self,table_info:TableInfoEntity):
        await self._session.add(TableInfoMapper.to_model(table_info))

    async def batch_add_table_infos(self,table_infos:list[TableInfoEntity]):
        await self._session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])

    async def update_table_info(self,table_info:TableInfoEntity):
        stmt = (update(TableInfoModel).where(TableInfoModel.id == table_info.id)
                .values(
                    name=table_info.name,
                    role=table_info.role,
                    description=table_info.description,
                )
        )
        await  self._session.execute(stmt)

    async def batch_update_table_infos(self,table_infos:list[TableInfoEntity]):
        stmt = update(TableInfoModel)
        await  self._session.execute(stmt, table_infos)