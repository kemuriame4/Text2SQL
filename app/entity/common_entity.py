"""业务实体的公共字段基类：逻辑删除标记 + 创建/修改审计信息。"""
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CommonBaseEntity:
    """
    做什么：被 TableInfoEntity / ColumnInfoEntity 继承，统一提供 5 个公共字段。
    字段：
    del_flag (str | None)：逻辑删除标记，默认 '0' 表示未删除。
    create_time (datetime | None)：创建时间，默认是 datetime.now()。
    create_by (str | None)：创建者，默认 None。
    update_time (datetime | None)：修改时间，默认是 datetime.now()。
    update_by (str | None)：修改者，默认 None。
    注意：默认值写的是 datetime.now() 而不是 lambda，所以它只在"类定义那一刻"求值一次。
    结果是所有实例的 create_time / update_time 都是同一个时间（程序启动时间），
    不是各自的创建时间。想拿到真实时间要写 field(default_factory=datetime.now)。
    """
    del_flag: str | None = '0'
    create_time: datetime | None = datetime.now()
    create_by: str | None = None
    update_time: datetime | None = datetime.now()
    update_by: str | None = None
