"""字段信息的元数据库访问层：对 t_column_info 做按 id 查询、单条/批量新增、单条/批量修改。"""
from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import ColumnInfoModel


class ColumnInfoMySqlRepository:
    """只管元数据库里的 t_column_info 一张表，不处理事务提交（由 service 控制）。"""

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

    async def get_column_info_by_id(self,id:str):
        """
        做什么：按主键查一条字段信息。
        参数：
        id (str)：字段主键，格式"表名.字段名"，如 dim_region.region_name。
        返回：
        ColumnInfoEntity：查到则返回转换后的实体。
        None：查不到时返回。
        """
        result :ColumnInfoModel = await  self.session.get(ColumnInfoModel,id)
        if result is None:
            return None
        return ColumnInfoMapper.to_entity(result)

    async def add_column_info(self,column_info:ColumnInfoEntity):
        """
        做什么：把一条字段信息加入当前会话（走 session.add）。
        参数：
        column_info (ColumnInfoEntity)：要新增的字段信息实体。
        返回：
        None。此刻还没发 SQL，要等事务提交才落库。
        注意：主键已存在时，在 commit 阶段抛 IntegrityError。
        """
        await self.session.add(ColumnInfoMapper.to_model(column_info))

    async def batch_add_column_infos(self,column_infos:list[ColumnInfoEntity]):
        """
        做什么：把一批字段信息一次性加入当前会话（走 session.add_all）。
        参数：
        column_infos (list[ColumnInfoEntity])：要新增的字段实体列表。
        返回：
        None。要等事务提交才落库。
        注意：声明为 async 但方法体内没有 await，实际是同步执行。
        """
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])

    async def update_column_info(self,column_info:ColumnInfoEntity):
        """
        做什么：按主键更新一条字段信息，只更新 name / role / description 三个字段。
        参数：
        column_info (ColumnInfoEntity)：至少要带 id，否则更新 0 行。
        返回：
        None。不返回影响行数；主键不存在时静默更新 0 行。
        注意：description 来源于 yaml 的字段说明；type / examples / alias 都不会被这条语句更新，
        也就是说改了数仓结构或改了别名字典，重跑程序也不会同步到已有记录。
        """
        stmt = (update(ColumnInfoModel).where(ColumnInfoModel.id == column_info.id)
                .values(
                    name=column_info.name,
                    role=column_info.role,
                    description=column_info.description,
                )
        )
        await  self.session.execute(stmt)

    async def batch_update_column_infos(self,column_infos:list[ColumnInfoEntity]):
        """
        做什么：按传入的字典列表批量更新字段信息。
        参数：
        column_infos (list[ColumnInfoEntity])：要更新的字段实体列表。
        返回：
        None。
        注意：① stmt 没有 where，靠传入字典做 executemany，字典里必须带主键 id；
              ② asdict 展开的是全部字段，所以 type / examples / alias 在这里反而会被更新，
              这和上面单条 update 的行为不一致，两处更新的字段范围不同。
        """
        stmt = update(ColumnInfoModel)
        column = [asdict(column_info) for column_info in column_infos]
        # for column_info in column_infos:
        await  self.session.execute(stmt, column)
