# 【文件作用】
# 这个文件负责读写 MySQL 的 t_column_metric 表（字段和指标的关联表：记录"哪个指标跟哪些字段有关"）。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 这张表是"联合主键"：要同时用 column_id 和 metric_id 两个值才能定位一条记录。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from sqlalchemy import update  # 导入 update：用来拼"更新数据"的 SQL 语句
from sqlalchemy.ext.asyncio import AsyncSession  # 导入异步会话类型（会话 session = 和数据库之间的一条连接通道）

from app.entity.column_metric_entity import ColumnMetricEntity  # 字段-指标关联实体（程序内部流转用）
from app.entity.metric_info_entity import MetricInfoEntity  # 【注意】这里导入了指标实体，但下面代码实际没用到
from app.mapper.column_metric_mapper import ColumnMetricMapper  # 转换器：负责 ColumnMetric 的 Entity 和 Model 互转
from app.mapper.metric_info_mapper import MetricInfoMapper  # 【注意】这里导入了指标转换器，但下面代码实际没用到
from app.model.column_metric_model import ColumnMetricModel  # 数据库模型（对应 t_column_metric 表）
from app.model.metric_info_model import MetricInfoModel  # 【注意】这里导入了指标模型，但下面代码实际没用到


class ColumnMetricMySqlRepository:  # 定义"字段-指标关联仓库"类，专门管 t_column_metric 这张表
    def __init__(self,session:AsyncSession):  # 构造方法：创建对象时传入一个数据库会话
        #设置为私有的session会话
        self.session = session  # 把会话存进对象里，后面每个方法都能拿来用

    async def get_table_info_by_id(self,column_id:str,metric_id:str) -> MetricInfoEntity:  # 按"字段 id + 指标 id"查一条关联记录
        # 【注意】方法名又是从"表信息仓库"复制来的 get_table_info_by_id，没改名；而且返回的其实是关联实体，类型注解却写成了 MetricInfoEntity
        result :ColumnMetricModel = await  self.session.get(  # await 等结果；get 按主键查，返回数据库模型
            ColumnMetricModel,  # 要查哪个模型（哪张表）
            {"column_id": column_id, "metric_id": metric_id}  # 联合主键要用字典把两个主键值都传进去
        )
        if result is None:  # 如果数据库里没有这条记录
            return None  # 返回 None，表示"没找到"
        return ColumnMetricMapper.to_entity(result)  # 把数据库模型转成实体对象再返回



    async def batch_insert_data(self,datas:list[ColumnMetricEntity]):  # 批量新增关联数据
        self.session.add_all([ColumnMetricMapper.to_model(data) for data in datas])  # 列表推导式：逐条转成模型，再一次性全部加入会话



    async def batch_update_data(self,datas:list[ColumnMetricEntity]):  # 批量更新关联数据
        stmt = update(ColumnMetricModel)  # 只写 update 表名、不写条件，具体匹配靠下面传进去的字典列表
        data_map = [asdict(data) for data in datas]  # 把每个实体转成字典，键名要对得上表里的字段名
        await  self.session.execute(stmt, data_map)  # 把"语句 + 一批参数字典"一起执行，完成批量更新