"""表信息的元数据库访问层：对 t_table_info 做按 id 查询、单条/批量新增、单条/批量修改。"""
from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.table_info_entity import TableInfoEntity
from app.mapper.table_info_mapper import TableInfoMapper
from app.model.table_info_model import TableInfoModel


class TableInfoMySqlRepository:
    """只管元数据库里的 t_table_info 一张表，不处理事务提交（由 service 控制）。"""

    def __init__(self,session:AsyncSession):
        """
        做什么：注入一个异步会话，后续所有方法都复用这一个会话。
        参数：
        session (AsyncSession)：由 service 打开并传入的会话。
        返回：
        无。
        """
        #设置为私有的session会话
        self.session = session

    async def get_table_info_by_id(self,id:str):
        """
        做什么：按主键查一条表信息。
        参数：
        id (str)：表主键，实际取值是表名，如 dim_region。
        返回：
        TableInfoEntity：查到则返回转换后的实体。
        None：查不到时返回。
        注意：session.get 会先查会话内的身份映射缓存，同一会话里刚 add 还没 flush 的对象也能查到。
        """
        result :TableInfoModel = await  self.session.get(TableInfoModel,id)
        if result is None:
            return None
        return TableInfoMapper.to_entity(result)

    async def add_table_info(self,table_info:TableInfoEntity):
        """
        做什么：把一条表信息加入当前会话（走 session.add）。
        参数：
        table_info (TableInfoEntity)：要新增的表信息实体。
        返回：
        None。此时还没有真正发 SQL，要等 service 结束事务块（commit）才落库。
        注意：主键已存在时，commit 阶段会抛 IntegrityError。
        """
        await self.session.add(TableInfoMapper.to_model(table_info))

    async def batch_add_table_infos(self,table_infos:list[TableInfoEntity]):
        """
        做什么：把一批表信息一次性加入当前会话（走 session.add_all）。
        参数：
        table_infos (list[TableInfoEntity])：要新增的表信息实体列表，不能传 None。
        返回：
        None。同样要等事务提交才落库。
        注意：方法声明是 async，但方法体内没有 await，实际是同步执行的；
        传空列表时什么也不做（不会报错）。
        """
        self.session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])

    async def update_table_info(self,table_info:TableInfoEntity):
        """
        做什么：按主键更新一条表信息，只更新 name / role / description 三个字段。
        参数：
        table_info (TableInfoEntity)：至少要带 id，否则 where 条件不成立、更新 0 行。
        返回：
        None。执行完不会告诉你影响了几行；主键不存在时静默更新 0 行，不报错。
        """
        stmt = (update(TableInfoModel).where(TableInfoModel.id == table_info.id)
                .values(
                    name=table_info.name,
                    role=table_info.role,
                    description=table_info.description,
                )
        )
        await  self.session.execute(stmt)

    async def batch_update_table_infos(self,table_infos:list[TableInfoEntity]):
        """
        做什么：按传入的字典列表批量更新表信息。
        参数：
        table_infos (list[TableInfoEntity])：要更新的表信息实体列表。
        返回：
        None。
        注意：① stmt 只有 update(Model) 没有 where，会把整个字典当参数集交给驱动做 executemany，
              所以字典里必须包含主键 id，否则报错或更新错行；
              ② 和上面的单条 update 不同，这里只更新字典里出现的字段，
              asdict 展开后包含全部字段（含 del_flag、create_time 等），
              这些公共字段会被实体的默认值覆盖掉。
        """
        stmt = update(TableInfoModel)
        tables = [asdict(table_info) for table_info in table_infos]
        await  self.session.execute(stmt, tables)
