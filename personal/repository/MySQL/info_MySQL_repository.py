from dataclasses import asdict
from sqlalchemy import update
from personal.entity.info_entity import MetricInfoEntity, TableInfoEntity
from personal.mapper.info_mapper import MetricInfoMapper, TableInfoMapper
from personal.model.info_model import MetricInfoModel, TableInfoModel
from sqlalchemy.ext.asyncio import AsyncSession


class TableInfoMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_table_info_by_id(self, id: str):
        result: TableInfoModel = self.session.get(TableInfoModel, id)
        if result is None:
            return None
        return TableInfoMapper.to_entity(result)

    def add_table_info(self, table_info: TableInfoEntity):
        self.session.add(TableInfoMapper.to_model(table_info))

    def batch_add_table_infos(self, table_infos: list[TableInfoEntity]):
        self.session.add_all([TableInfoMapper.to_model for table_info in table_infos])

    async def update_table_info(self, table_info: TableInfoEntity):
        stmt = (
            update(TableInfoModel)
            .where(TableInfoModel.id == table_info.id)
            .values(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
            )
        )
        await self.session.execute(stmt)

    async def batch_update_table_infos(self, table_infos: list[TableInfoEntity]):
        stmt = update(TableInfoModel)
        tables = [asdict(table_info) for table_info in table_infos]
        await self.session.execute(stmt, tables)


class MetricMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_table_info_by_id(self, id: str):
        result: MetricInfoModel = self.session.get(MetricInfoModel, id)
        if result is None:
            return None
        return MetricInfoMapper.to_entity(result)

    def batch_insert_data(self, datas: list[MetricInfoEntity]):
        self.session.add_all([MetricInfoMapper.to_model(data) for data in datas])

    async def batch_update_data(self, datas: list[MetricInfoEntity]):
        stmt = update(MetricInfoModel)
        data_map = [asdict(data) for data in datas]
        await self.session.execute(stmt, data_map)
