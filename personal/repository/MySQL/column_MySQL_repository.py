from personal.entity.info_entity import MetricInfoEntity
from personal.entity.column_entity import ColumnInfoEntity, ColumnMetricEntity
from personal.mapper.column_mapper import ColumnInfoMapper, ColumnMetricMapper
from personal.model.column_model import ColumnInfoModel, ColumnMetricModel
from dataclasses import asdict
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


class ColumnInfoMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_info_by_id(self, id: str):
        result: ColumnInfoModel = await self.session.get(ColumnInfoModel, id)
        if result is None:
            return None
        return ColumnInfoMapper.to_entity(result)

    def add_column_info(self, column_info: ColumnInfoEntity):
        self.session.add(ColumnInfoMapper.to_model(column_info))

    def batch_add_column_infos(self, column_infos: list[ColumnInfoEntity]):
        self.session.add_all(
            [ColumnInfoMapper.to_model(column_info) for column_info in column_infos]
        )

    async def update_column_info(self, column_info: ColumnInfoEntity):
        stmt = (
            update(ColumnInfoModel)
            .where(ColumnInfoModel.id == column_info.id)
            .values(
                name=column_info.name,
                role=column_info.role,
                description=column_info.description,
            )
        )
        await self.session.execute(stmt)

    async def batch_update_column_infos(self, column_infos: list[ColumnInfoEntity]):
        stmt = update(ColumnInfoModel)
        columns = [asdict(column_info) for column_info in column_infos]
        await self.session.execute(stmt, columns)


class ColumnMetricMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_table_info_by_id(self, column_id: str, metric_id: str) -> MetricInfoEntity:
        result: ColumnMetricModel = await self.session.get(
            ColumnMetricModel, {"column_id": column_id, "metric_id": metric_id}
        )
        if result is None:
            return None
        return ColumnMetricMapper.to_entity(result)

    def batch_add_column_infos(self, datas: list[ColumnMetricEntity]):
        self.session.add_all([ColumnMetricMapper.to_model(data) for data in datas])

    async def batch_update_datas(self, datas: list[ColumnMetricEntity]):
        stmt = update(ColumnMetricModel)
        data_map = [asdict(data) for data in datas]
        await self.session.execute(stmt, data_map)
