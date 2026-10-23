# 脚本的入口
"""元数据初始化脚本入口：定位配置文件，创建 service，跑一次元数据构建。"""
import asyncio
from pathlib import Path

from app.service.meta_service import MetaService


async def async_main():
    '''
        初始化业务逻辑层对象
        调用业务逻辑层
    '''
    # 做什么：定位 meta_config.yaml 并调用 service.build() 完成一次元数据构建。
    # 参数：无。
    # 返回：None。执行结果体现在元数据库和终端打印上。
    # 注意：parents[2] 指项目根目录（MC_App / Text2SQL1021），改目录层级会找不到 yaml。
    file_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'
    service = MetaService()
    await  service.build(file_path)


'''
程序入口
    因为代码使用异步编程
    所以main 方法需要使用asyncio.run 来调用异步方法
'''
if __name__ == '__main__':
    asyncio.run(async_main())   # 启动事件循环，把协程跑起来
