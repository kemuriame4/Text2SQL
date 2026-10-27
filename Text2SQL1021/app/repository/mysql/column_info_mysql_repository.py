# 【文件作用】
# 这个文件负责把"字段信息"写进 / 读出自 MySQL 的 t_column_info 表。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 除了常规的增删改查，它还提供一个专用查询：按表 id 查出这张表的主键字段和外键字段。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from sqlalchemy import update, text  # update 用来拼更新语句；text 用来直接执行手写的原生 SQL
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步会话类型（会话 session = 和数据库之间的一条连接通道）

from app.entity.column_info_entity import ColumnInfoEntity  # 字段信息实体（程序内部流转用）
from app.mapper.column_info_mapper import ColumnInfoMapper  # 转换器：负责 Entity 和 Model 之间的互转
from app.model.column_info_model import ColumnInfoModel  # 数据库模型（对应 t_column_info 表）
from app.utils.json_parser_util import _parse_json_field  # 工具函数：把数据库里存的 JSON 字符串解析回列表等结构


class ColumnInfoMySqlRepository:  # 定义"字段信息仓库"类，专门管 t_column_info 这张表
    def __init__(self,session:AsyncSession):  # 构造方法：创建对象时传入一个数据库会话
        #设置为私有的session会话
        self.session = session  # 把会话存进对象里，后面每个方法都能拿来用

    async def get_column_info_by_id(self,id:str):  # 异步（发出去不用干等结果）按主键 id 查一条字段信息
        result :ColumnInfoModel = await  self.session.get(ColumnInfoModel,id)  # await 等结果；get 按主键查，返回数据库模型
        if result is None:  # 如果数据库里没有这条记录
            return None  # 返回 None，表示"没找到"
        return ColumnInfoMapper.to_entity(result)  # 把数据库模型转成实体对象再返回

    async def add_column_info(self,column_info:ColumnInfoEntity):  # 新增一条字段信息
        await self.session.add(ColumnInfoMapper.to_model(column_info))  # 实体先转成数据库模型，再交给会话（等统一提交才真正落库）

    async def batch_add_column_infos(self,column_infos:list[ColumnInfoEntity]):  # 批量新增字段信息
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])  # 列表推导式：逐条转模型，再一次性全部加入会话

    async def update_column_info(self,column_info:ColumnInfoEntity):  # 按 id 更新一条字段信息（只改 name / role / description 三列）
        stmt = (update(ColumnInfoModel).where(ColumnInfoModel.id == column_info.id)  # 拼 SQL：update 表，条件是 id 等于传进来的 id
                .values(  # 指定要改成什么值
                    name=column_info.name,  # 新的字段名
                    role=column_info.role,  # 新的字段角色（比如主键 / 外键 / 普通字段）
                    description=column_info.description,  # 新的字段描述
                )
        )
        await  self.session.execute(stmt)  # 执行这条 update 语句

    async def batch_update_column_infos(self,column_infos:list[ColumnInfoEntity]):  # 批量更新字段信息
        stmt = update(ColumnInfoModel)  # 只写 update 表名、不写条件，具体匹配靠下面传进去的字典列表
        column = [asdict(column_info) for column_info in column_infos]  # 把每个实体转成字典，键名要对得上表里的字段名
        # for column_info in column_infos:
        await  self.session.execute(stmt, column)  # 把"语句 + 一批参数字典"一起执行，完成批量更新

    async  def get_key_by_table_id(self,table_id:str)->list[ColumnInfoEntity]:  # 按表 id 查出这张表的所有"主键 + 外键"字段
        # 【注意】下面 sql 用三引号多行字符串包裹，里面的 SQL 内容不能动，所以说明只写在这行上面
        sql ="""
        select * from t_column_info
        where table_id = :table_id
        and role in ('primary_key','foreign_key')
        """
        result = await self.session.execute(text(sql),{"table_id":table_id})  # 执行原生 SQL；:table_id 用字典里的值替换（这样传参能防 SQL 注入）
        rows = result.mappings().fetchall()  # 把结果按"列名 -> 值"的字典形式一次性全部取出来
        entities = []  # 准备一个空列表，用来装转换后的实体
        for row in rows:  # 一行一行遍历查询结果
            data = dict(row)  # 把当前这一行转成普通字典
            data["alias"] = _parse_json_field(data.get("alias"))  # 数据库里 alias 存的是 JSON 字符串，要解析成列表
            data["examples"] = _parse_json_field(data.get("examples"))  # examples 同理，也解析成列表
            entities.append(ColumnInfoEntity(**data))  # 用字典里的字段构造实体对象，加入列表
        return entities  # 返回这张表所有的主键 / 外键字段
