from  datetime import  datetime
from dataclasses import dataclass, field


@dataclass
class CommonBaseEntity:
    '''
        所有业务实体的公共字段
        【坑】datetime.now() 写成默认"值"，会在类定义那一刻就求值一次，
              之后所有实例共享同一个时间；必须用 field(default_factory=datetime.now)。
        '''

    del_flag:str | None = '0'
    create_time: datetime | None = field(default_factory=datetime.now)
    create_by:str | None ='system'
    update_time: datetime | None = field(default_factory=datetime.now)
    update_by: str | None  = 'system'

    # 这段代码用dataclass
    # 定义了一个公共字段基类，目的是让所有业务实体继承它，自动拥有
    # del_flag、create_time、create_by、update_time、update_by
    # 这五个审计字段。