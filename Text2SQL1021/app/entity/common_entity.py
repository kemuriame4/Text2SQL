# 【文件作用】
# 这个文件定义所有 entity（代码里装数据的"盒子"）共用的公共字段：是否删除、谁在什么时候创建/修改。
# 它不连数据库，只用于在代码各层之间传递数据；数据库那一侧对应 app/model/common_base.py。
from datetime import datetime  # 导入 datetime（日期时间类型，用来表示"哪年哪月哪日几点几分"）
from dataclasses import dataclass  # 导入 dataclass（Python 自带的一种"纯数据盒子"写法，写字段就行，不用自己写初始化函数）


@dataclass  # 套上 dataclass 装饰器：自动生成 __init__ 等样板方法，写字段就行
class CommonBaseEntity:  # 定义"公共基础 entity"类，其他 entity 继承它就能自动拥有下面这 5 个字段
    del_flag: str | None = '0'  # 是否删除：'0' 表示未删除、'1' 表示已删除（软删除，数据不真删只打标记）；str | None 表示要么是字符串要么是空
    create_time: datetime | None = datetime.now()  # 【注意】创建时间：这种写法会在"类定义时"就执行一次并固定下来，导致所有对象共用同一个时刻；正确写法应是 field(default_factory=datetime.now)，让每个对象创建时再取当前时间
    create_by: str | None = None  # 创建人：谁插入的这条数据，默认空
    update_time: datetime | None = datetime.now()  # 【注意】修改时间：同样会在类定义时就固定，所有对象共用同一时刻；正确写法应是 field(default_factory=datetime.now)
    update_by: str | None = None  # 修改人：谁最后改的这条数据，默认空
