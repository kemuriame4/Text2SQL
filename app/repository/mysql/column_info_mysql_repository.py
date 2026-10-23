from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        # 设置为私有的session会话
        self._session = session

    async def  get_column_info_by_id(self,id:str):
        '''
        根据id获得信息
        '''
        result: ColumnInfoModel = await self._session.get(ColumnInfoModel,id)
        if result is None:
            return None

        # 查到的是数据实体，需要返回业务实体，需要转换
        return ColumnInfoMapper.to_entity(result)

    async def add_column_info(self,column_info:ColumnInfoEntity):
        '''
        新增column_info
        '''
        await self._session.add(ColumnInfoMapper.to_model(column_info))

    async def batch_add_column_info(self,column_info_list:list[ColumnInfoEntity]):
        '''
        批量新增column_info
        '''
        await self._session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_info_list])

    async def update_column_info(self,column_info:ColumnInfoEntity):
        '''
        修改
        '''
        stmt = (update(ColumnInfoModel).where(ColumnInfoModel.id == column_info.id)
                .values(
            name=column_info.name,
            role=column_info.role,
            description=column_info.description,
            type=column_info.type,
            alias=column_info.alias,
            table_id=column_info.table_id,
            examples=column_info.examples
        ))
        await self._session.execute(stmt)

    async def batch_update_column_info(self,column_info_list:list[ColumnInfoEntity]):
        '''
        批量修改
        '''
        stmt = update(ColumnInfoModel)
        column = [asdict(column_info) for column_info in column_info_list]
        await self._session.execute(stmt, column_info_list)