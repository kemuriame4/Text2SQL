from dataclasses import asdict

from sqlalchemy import update, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.table_info_model import TableInfoModel


class TableInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        #设置为私有的session会话
        self.session = session

    async def get_table_info_by_id(self,id:str):
        result :TableInfoModel = await  self.session.get(TableInfoModel,id)
        if result is None:
            return None
        return TableInfoMapper.to_entity(result)

    async def add_table_info(self,table_info:TableInfoEntity):
        await self.session.add(TableInfoMapper.to_model(table_info))

    async def batch_add_table_infos(self,table_infos:list[TableInfoEntity]):
        self.session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])

    async def update_table_info(self,table_info:TableInfoEntity):
        stmt = (update(TableInfoModel).where(TableInfoModel.id == table_info.id)
                .values(
                    name=table_info.name,
                    role=table_info.role,
                    description=table_info.description,
                )
        )
        await  self.session.execute(stmt)

    async def batch_update_table_infos(self,table_infos:list[TableInfoEntity]):
        '''
        批量更新表信息
        【原写法的问题】update(TableInfoModel) 没有 where，参数里又带着主键 id，
        编译出来是「不带 WHERE 的 UPDATE」，会把整张表刷成同一条数据，
        第二批还会主键冲突。必须 where(id == bindparam('id'))。
        【第二个坑】ORM 层的批量 UPDATE 一旦带了额外 WHERE，SQLAlchemy 无法同步
        会话里已加载的对象，会抛 InvalidRequestError，所以要显式关掉 synchronize_session。
        【第三个坑】where 里的 bindparam 不能叫 'id'——这个名字在 UPDATE 的 SET 子句里
        是保留的，必须换个名字（这里用 b_id），参数字典里再单独塞一份。
        '''
        stmt = (update(TableInfoModel)
                .where(TableInfoModel.id == bindparam('b_id'))
                .values(
                    name=bindparam('name'),
                    role=bindparam('role'),
                    description=bindparam('description'),
                    update_time=bindparam('update_time'),
                    update_by=bindparam('update_by'),
                    del_flag=bindparam('del_flag'),
                ))
        tables = [{**asdict(table_info), 'b_id': table_info.id}
                  for table_info in table_infos]
        await self.session.execute(
            stmt.execution_options(synchronize_session=False), tables)