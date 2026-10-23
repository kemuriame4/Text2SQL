from dataclasses import asdict

from sqlalchemy import update, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        #设置为私有的session会话
        self.session = session

    async def get_column_info_by_id(self,id:str):
        result :ColumnInfoModel = await  self.session.get(ColumnInfoModel,id)
        if result is None:
            return None
        return ColumnInfoMapper.to_entity(result)

    async def add_column_info(self,column_info:ColumnInfoEntity):
        await self.session.add(ColumnInfoMapper.to_model(column_info))

    async def batch_add_column_infos(self,column_infos:list[ColumnInfoEntity]):
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])

    async def update_column_info(self,column_info:ColumnInfoEntity):
        stmt = (update(ColumnInfoModel).where(ColumnInfoModel.id == column_info.id)
                .values(
                    name=column_info.name,
                    role=column_info.role,
                    description=column_info.description,
                )
        )
        await  self.session.execute(stmt)

    async def batch_update_column_infos(self,column_infos:list[ColumnInfoEntity]):
        '''
        批量更新字段信息（同样必须带 where，否则整表被刷；
        同样要 synchronize_session=False，否则 ORM 会抛 InvalidRequestError）
        '''
        stmt = (update(ColumnInfoModel)
                # bindparam 不能叫 'id'（与 SET 子句保留名冲突），用 b_id
                .where(ColumnInfoModel.id == bindparam('b_id'))
                .values(
                    name=bindparam('name'),
                    role=bindparam('role'),
                    description=bindparam('description'),
                    type=bindparam('type'),
                    alias=bindparam('alias'),
                    examples=bindparam('examples'),
                    table_id=bindparam('table_id'),
                    update_time=bindparam('update_time'),
                    update_by=bindparam('update_by'),
                    del_flag=bindparam('del_flag'),
                ))
        column = [{**asdict(column_info), 'b_id': column_info.id}
                  for column_info in column_infos]
        await self.session.execute(
            stmt.execution_options(synchronize_session=False), column)