# 【文件作用】
# 这个文件负责把"指标信息"写进 / 读出自 MySQL 的 t_metric_info 表。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 指标 = 业务上的统计口径，比如"销售额""订单量"。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from sqlalchemy import update  # 导入 update：用来拼"更新数据"的 SQL 语句
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步会话类型（会话 session = 和数据库之间的一条连接通道）

from app.entity.metric_info_entity import MetricInfoEntity  # 指标实体（程序内部流转用的对象）
from app.mapper.metric_info_mapper import MetricInfoMapper  # 转换器：负责 Entity 和 Model 之间的互转
from app.model.metric_info_model import MetricInfoModel  # 数据库模型（对应 t_metric_info 表）


class MetricInfoMySqlRepository:  # 定义"指标信息仓库"类，专门管 t_metric_info 这张表
    def __init__(self,session:AsyncSession):  # 构造方法：创建对象时传入一个数据库会话
        #设置为私有的session会话
        self.session = session  # 把会话存进对象里，后面每个方法都能拿来用

    async def get_table_info_by_id(self,id:str):  # 异步（发出去不用干等结果）按主键 id 查一条指标信息
        # 【注意】方法名还叫 get_table_info_by_id，是从"表信息仓库"复制过来忘了改名的；它实际查的是"指标"
        result :MetricInfoModel = await  self.session.get(MetricInfoModel,id)  # await 等结果；get 按主键查，返回数据库模型
        if result is None:  # 如果数据库里没有这条记录
            return None  # 返回 None，表示"没找到"
        return MetricInfoMapper.to_entity(result)  # 把数据库模型转成实体对象再返回



    async def batch_insert_data(self,datas:list[MetricInfoEntity]):  # 批量新增指标数据
        self.session.add_all([MetricInfoMapper.to_model(data) for data in datas])  # 列表推导式：逐条转成模型，再一次性全部加入会话



    async def batch_update_data(self,datas:list[MetricInfoEntity]):  # 批量更新指标数据
        stmt = update(MetricInfoModel)  # 只写 update 表名、不写条件，具体匹配靠下面传进去的字典列表
        data_map = [asdict(data) for data in datas]  # 把每个实体转成字典，键名要对得上表里的字段名
        await  self.session.execute(stmt, data_map)  # 把"语句 + 一批参数字典"一起执行，完成批量更新