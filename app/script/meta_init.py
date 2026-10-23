# 脚本的入口：把 conf/meta_config.yaml 里的元数据写进 MySQL
import asyncio
import sys
from pathlib import Path

# 【坑】直接 `python app/script/meta_init.py` 运行时，sys.path[0] 是 app/script 目录，
#       下面的 from app.xxx import ... 会报 ModuleNotFoundError。
#       把项目根目录加进 sys.path 后，两种运行方式都能用：
#           python app/script/meta_init.py
#           python -m app.script.meta_init
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.service.meta_service import MetaService


async def async_main():
    '''
        初始化业务逻辑层对象
        调用业务逻辑层
    '''
    file_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'
    service = MetaService()
    await  service.build(file_path)


'''
程序入口
    因为代码使用异步编程
    所以main 方法需要使用asyncio.run 来调用异步方法
'''
if __name__ == '__main__':
    asyncio.run(async_main())
