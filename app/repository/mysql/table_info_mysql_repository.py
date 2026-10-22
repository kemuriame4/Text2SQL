
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.column_info_model import ColumnInfoModel
from app.model.table_info_model import TableInfoModel


class TableInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        # 设置为私有的session会话
        self._session = session

    async def  get_table_info_by_id(self,id:str):
        '''
        根据id获得信息
        '''
        result: TableInfoModel = await self._session.get(TableInfoModel,id)
        if result is None:
            return None

        # 查到的是数据实体，需要返回业务实体，需要转换
        return TableInfoMapper.to_entity(result)

    async def add_table_info(self,table_info:TableInfoEntity):
        '''
        新增table_info
        '''
        await self._session.add(TableInfoMapper.to_model(table_info))

    async def batch_add_table_info(self,table_info_list:list[TableInfoEntity]):
        '''
        批量新增table_info
        '''
        await self._session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_info_list])

    async def update_table_info(self,table_info:TableInfoEntity):
        '''
        修改
        '''
        stmt = (update(TableInfoModel).where(TableInfoModel.id == table_info.id)
                .values(
            name=table_info.name,
            role=table_info.role,
            description=table_info.description,
        ))
        await self._session.execute(stmt)

    async def batch_update_table_info(self,table_info_list:list[TableInfoEntity]):
        '''
        批量修改
        '''
        stmt = update(TableInfoModel)
        await self._session.execute(stmt, table_info_list)