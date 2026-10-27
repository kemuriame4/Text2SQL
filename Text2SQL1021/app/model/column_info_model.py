# 【文件作用】
# 这个文件是数据库表 t_column_info（字段信息表）在代码里的镜像（model）。
# repository 层通过它读写数据库；代码各层之间传数据用 app/entity/column_info_entity.py。
from sqlalchemy import String, CHAR, Text, JSON  # 导入列类型：String 变长字符串、CHAR 定长字符串（未用到）、Text 长文本、JSON 结构化数据
from sqlalchemy.orm import Mapped, mapped_column  # 导入 Mapped（标注 Python 类型）和 mapped_column（定义数据库列）

from app.model.common_base import CommonBase  # 导入公共 model 基类，获得公共列

class ColumnInfoModel(CommonBase):  # 定义字段信息 model 类，对应数据库里的 t_column_info 表
    __tablename__ = 't_column_info'  # 指定这个类映射的真实表名
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')  # 主键 id：唯一标识一个字段；primary_key=True 表示主键
    name:Mapped[str] = mapped_column(String(64),comment='名称')  # 字段名称：这一列叫什么，最长 64 字符
    role:Mapped[str] = mapped_column(String(32),comment='列类型(primary_key,foreign_key,measure,dimension)')  # 字段角色：主键 / 外键 / 度量 / 维度
    description:Mapped[str] = mapped_column(Text,comment='描述')  # 字段描述：这一列的业务含义，用 Text 存长文本
    examples:Mapped[str] = mapped_column(JSON,comment='数据示例')  # 数据示例：这一列真实数据长什么样，JSON 类型（数据库里能存一段结构化数据的字段）
    type:Mapped[str] = mapped_column(String(64),comment='数据类型')  # 数据类型：如 varchar/int/decimal
    alias:Mapped[str] = mapped_column(JSON,comment='别名')  # 别名：这一列的其他叫法，JSON 类型（存数组）
    table_id:Mapped[str] = mapped_column(String(32),comment='表id')  # 所属表 id（外键，指向 t_table_info.id）
    qdrant_id:Mapped[str] = mapped_column(String(32),comment='表id')  # 【注意】qdrant_id 原本是向量库里的 id，但 mysql/initmysql 的 t_column_info 建表语句里没有这一列，一旦往库里写就会报"未知列"；另外这里的 comment 写成"表id"是复制粘贴留下的



