# 脚本的入口
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.service.base_init_service import BaseInitService


async def async_main():
    '''
        初始化业务逻辑层对象
        调用业务逻辑层
    '''
    file_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'
    service = BaseInitService()
    await service.build(file_path)


'''
程序入口
    因为代码使用异步编程
    所以main 方法需要使用asyncio.run 来调用异步方法
'''
if __name__ == '__main__':
    asyncio.run(async_main())