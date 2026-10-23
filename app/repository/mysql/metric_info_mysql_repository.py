from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.metric_info_entity import MetricInfoEntity
from app.mapper.metric_info_mapper import MetricInfoMapper
from app.model.metric_info_model import MetricInfoModel


class MetricInfoMySqlRepository:
    def __init__(self,session:AsyncSession):
        #设置为私有的session会话
        self.session = session

    async def get_table_info_by_id(self,id:str):
        result :MetricInfoModel = await  self.session.get(MetricInfoModel,id)
        if result is None:
            return None
        return MetricInfoMapper.to_entity(result)



    async def batch_insert_data(self,datas:list[MetricInfoEntity]):
        self.session.add_all([MetricInfoMapper.to_model(data) for data in datas])



    async def batch_update_data(self,datas:list[MetricInfoEntity]):
        stmt = update(MetricInfoModel)
        data_map = [asdict(data) for data in datas]
        await  self.session.execute(stmt, data_map)