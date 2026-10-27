# 【文件作用】
# 这个文件负责把"表信息"写进 / 读出自 MySQL 的 t_table_info 表。
# 属于 repository 层（数据读写层，相当于仓库管理员），往上被 service 或 agent 节点调用。
# 它把数据库里的表记录（Model）和程序里流转的对象（Entity）互相翻译后存取。
# 注：Model = 和数据库表一一对应的类；Entity = 程序内部传递数据用的类。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from sqlalchemy import update  # 导入 update：用来拼"更新数据"的 SQL 语句
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步会话类型（会话 session = 和数据库之间的一条连接通道）

from app.entity.table_info_entity import TableInfoEntity  # 表信息实体（程序内部流转用的对象）
from app.mapper.table_info_mapper import TableInfoMapper  # 转换器：负责 Entity 和 Model 之间的互转
from app.model.table_info_model import TableInfoModel  # 数据库模型（和 t_table_info 表一一对应）


class TableInfoMySqlRepository:  # 定义"表信息仓库"类，专门管 t_table_info 这张表
    def __init__(self,session:AsyncSession):  # 构造方法：创建对象时传入一个数据库会话
        #设置为私有的session会话
        self.session = session  # 把会话存进对象里，后面每个方法都能拿来用

    async def get_table_info_by_id(self,id:str):  # 异步（发出去不用干等结果，可以先干别的）按主键 id 查一条表信息
        result :TableInfoModel = await  self.session.get(TableInfoModel,id)  # await 等查询结果回来；get 是按主键查，返回数据库模型
        if result is None:  # 如果数据库里没有这条记录（查出来是空）
            return None  # 直接返回 None，表示"没找到"
        return TableInfoMapper.to_entity(result)  # 把数据库模型转成实体对象再返回

    async def add_table_info(self,table_info:TableInfoEntity):  # 新增一条表信息
        await self.session.add(TableInfoMapper.to_model(table_info))  # 先把实体转成数据库模型，再交给会话（此时还没真正写库，要等统一提交）

    async def batch_add_table_infos(self,table_infos:list[TableInfoEntity]):  # 批量新增多条表信息
        self.session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])  # 列表推导式：逐条转成模型，再一次性全部加入会话

    async def update_table_info(self,table_info:TableInfoEntity):  # 按 id 更新一条表信息（只改 name / role / description 三列）
        stmt = (update(TableInfoModel).where(TableInfoModel.id == table_info.id)  # 拼 SQL：update 表，条件是 id 等于传进来的 id
                .values(  # 指定要改成什么值
                    name=table_info.name,  # 新的表名
                    role=table_info.role,  # 新的表角色（事实表 / 维度表）
                    description=table_info.description,  # 新的表描述
                )
        )
        await  self.session.execute(stmt)  # 执行这条 update 语句

    async def batch_update_table_infos(self,table_infos:list[TableInfoEntity]):  # 批量更新多条表信息
        stmt = update(TableInfoModel)  # 只写 update 表名、不写具体条件，具体匹配靠下面传进去的字典列表
        tables = [asdict(table_info) for table_info in table_infos]  # 把每个实体转成字典，字典的键名要对得上表里的字段名
        await  self.session.execute(stmt, tables)  # 把"语句 + 一批参数字典"一起执行，完成批量更新