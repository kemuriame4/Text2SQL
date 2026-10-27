from dataclasses import asdict

from sqlalchemy import update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_info_entity import ColumnInfoEntity
from app.mapper.column_info_mapper import ColumnInfoMapper
from app.model.column_info_model import ColumnInfoModel
from app.utils.json_parser_util import _parse_json_field


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
        stmt = update(ColumnInfoModel)
        column = [asdict(column_info) for column_info in column_infos]
        # for column_info in column_infos:
        await  self.session.execute(stmt, column)

    async  def get_key_by_table_id(self,table_id:str)->list[ColumnInfoEntity]:
        sql ="""
        select * from t_column_info
        where table_id = :table_id
        and role in ('primary_key','foreign_key')
        """
        result = await self.session.execute(text(sql),{"table_id":table_id})
        rows = result.mappings().fetchall()
        entities = []
        for row in rows:
            data = dict(row)
            data["alias"] = _parse_json_field(data.get("alias"))
            data["examples"] = _parse_json_field(data.get("examples"))
            entities.append(ColumnInfoEntity(**data))
        return entities

