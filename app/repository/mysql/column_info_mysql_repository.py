from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import  ColumnInfoModel

class ColumnInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def get_column_info_by_id(self,id:str):
        result:ColumnInfoModel = await self.session.get(ColumnInfoModel,id)

        if result is None:
            return None
        return ColumnInfoMapper.to_entity(result)

    async def add_column_ifo(self,column_ifo:ColumnInfoEntity):
        await self.session.add(ColumnInfoMapper.to_model(column_ifo))

    async def batch_add_column_infos(self,column_infos:list[ColumnInfoEntity]):
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])

    async def update_column_info(self,column_info:ColumnInfoEntity):
        stmt = (update(ColumnInfoModel).where(ColumnInfoModel.id == column_info.id)
                .values(
                    name = column_info.name,
                    role = column_info.role,
                    description = column_info.description
                ))
        await self.session.execute(stmt)

    async def batch_update_column_infos(self,column_infos:list[ColumnInfoEntity]):
        stmt = update(ColumnInfoModel)
        column = [asdict(column_info) for column_info in column_infos]
        await self.session.execute(stmt,column)