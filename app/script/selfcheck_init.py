"""离线自检：不连 MySQL/Qdrant，用内存 sqlite 验证元数据入库逻辑（新增 + 更新两条路径）。
运行：python app/script/selfcheck_init.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.conf.mate_config import MateConfig
from app.model.column_info_model import ColumnInfoModel
from app.model.common_base import CommonBase
from app.repository.column_info_repository import ColumnInfoMySqlRepository
from app.repository.table_info_repository import TableInfoMySqlRepository
from app.service.base_init_service import BaseInitService
from app.utils.load_config_util import load_config


class FakeDwRepository:
    """假装数据仓库：返回固定字段类型和示例数据"""

    async def get_column_type_by_name(self, name):
        return {"region_id": "int", "province": "varchar(32)", "region_name": "varchar(32)", "country": "varchar(32)"}

    async def get_column_values(self, table_name, column, limit=5):
        return ["广东", "江苏"]


class FakeTx:
    def __init__(self, session: Session):
        self._session = session
        self._tx = None

    async def __aenter__(self):
        self._tx = self._session.begin()
        return self._tx

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._tx.commit()
        else:
            self._tx.rollback()
        return False


class FakeAsyncSession:
    """把同步 Session 包成仓储需要的异步接口，仅用于自检"""

    def __init__(self, session: Session):
        self._session = session

    def begin(self):
        return FakeTx(self._session)

    async def get(self, model, ident):
        return self._session.get(model, ident)

    def add(self, obj):
        self._session.add(obj)

    def add_all(self, objs):
        self._session.add_all(objs)

    async def execute(self, stmt, params=None):
        return self._session.execute(stmt) if params is None else self._session.execute(stmt, params)


async def main():
    engine = create_engine("sqlite://")
    CommonBase.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    config: MateConfig = load_config(Path(__file__).parents[2] / "conf" / "meta_config.yaml", MateConfig)
    tables = [t for t in config.tables if t.name == "dim_region"]

    svc = BaseInitService()
    fake = FakeAsyncSession(session)
    svc._table_info_mysql_repository = TableInfoMySqlRepository(fake)
    svc._column_info_mysql_repository = ColumnInfoMySqlRepository(fake)
    svc._dw_mysql_repository = FakeDwRepository()

    # 第一次：全部新增
    infos = await svc._save_table_tomysql(tables)
    assert len(infos) == 4, f"新增字段数应为 4，实际 {len(infos)}"
    assert {i.id for i in infos} == {f"dim_region.{c.name}" for c in tables[0].columns}
    assert infos[0].type == "int" and infos[0].examples == ["广东", "江苏"]

    # 第二次：全部更新，不能重复插入，描述要同步
    tables[0].description = "改过的描述"
    table_column = [c for c in tables[0].columns if c.name == "province"][0]
    table_column.description = "改过的字段描述"
    infos = await svc._save_table_tomysql(tables)
    assert len(infos) == 4, f"更新字段数应为 4，实际 {len(infos)}"

    row = await svc._table_info_mysql_repository.get_table_info_by_id("dim_region")
    assert row.description == "改过的描述", row.description
    column = await svc._column_info_mysql_repository.get_column_info_by_id("dim_region.province")
    assert column.alias == ["省份", "省", "所在省份"], column.alias
    assert column.description == "改过的字段描述", column.description
    total = session.execute(select(ColumnInfoModel)).fetchall()
    assert len(total) == 4, f"t_column_info 应有 4 行，实际 {len(total)}"
    print("自检通过：新增 4 字段 → 更新 4 字段，无重复行，描述/别名一致")


asyncio.run(main())
