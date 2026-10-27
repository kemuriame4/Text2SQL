# 【文件作用】
# 这个文件是数据库表 t_table_info（表信息表）在代码里的镜像（model）。
# repository 层通过它读写数据库；代码各层之间传数据用 app/entity/table_info_entity.py。
from sqlalchemy import String, CHAR  # 从 SQLAlchemy 导入列类型：String 变长字符串、CHAR 定长字符串（本文件 CHAR 没用到，保留原样）
from sqlalchemy.orm import Mapped, mapped_column  # 导入 Mapped（标注 Python 类型）和 mapped_column（定义数据库列）

from app.model.common_base import CommonBase  # 导入公共 model 基类，获得 del_flag/创建人/修改人等公共列


class TableInfoModel(CommonBase):  # 定义表信息 model 类，对应数据库里的 t_table_info 表
    __tablename__ = 't_table_info'  # 指定这个类映射的真实表名（SQLAlchemy 靠它找到表）
    id:Mapped[str] = mapped_column(String(32),primary_key=True,comment='主键id')  # 主键 id：唯一标识一张表；primary_key=True 表示主键（唯一标识一条记录的字段）
    name:Mapped[str] = mapped_column(String(64),comment='名称')  # 表名称：这张表叫什么，最长 64 字符
    role:Mapped[str] = mapped_column(String(64),comment='角色 0:维度表  1 事实表 ')  # 表角色：0 维度表、1 事实表；【注意】数据库里 role 是 char(1)，这里却写成 String(64)，长度定义不一致
    description:Mapped[str] = mapped_column(String(255),comment='描述')  # 表描述：这张表是干什么的，最长 255 字符


