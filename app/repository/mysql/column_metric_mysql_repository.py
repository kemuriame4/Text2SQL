from dataclasses import asdict

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.entity.column_metric_entity import ColumnMetricEntity
from app.entity.metric_info_entity import MetricInfoEntity
from app.mapper.column_metric_mapper import ColumnMetricMapper
from app.mapper.metric_info_mapper import MetricInfoMapper
from app.model.column_metric_model import ColumnMetricModel
from app.model.metric_info_model import MetricInfoModel


class ColumnMetricMySqlRepository:
    def __init__(self,session:AsyncSession):
        #设置为私有的session会话
        self.session = session

    async def get_table_info_by_id(self,column_id:str,metric_id:str) -> MetricInfoEntity:
        result :ColumnMetricModel = await  self.session.get(
            ColumnMetricModel,
            {"column_id": column_id, "metric_id": metric_id}
        )
        if result is None:
            return None
        return ColumnMetricMapper.to_entity(result)



    async def batch_insert_data(self,datas:list[ColumnMetricEntity]):
        self.session.add_all([ColumnMetricMapper.to_model(data) for data in datas])



    async def batch_update_data(self,datas:list[ColumnMetricEntity]):
        stmt = update(ColumnMetricModel)
        data_map = [asdict(data) for data in datas]
        await  self.session.execute(stmt, data_map)