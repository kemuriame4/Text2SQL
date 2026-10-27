# 【文件作用】
# 这是离线建库的启动入口：运行这个脚本，就会把 conf/meta_config.yaml 里写的表/字段/指标元数据，
# 交给 MetaService.build() 去写入 MySQL（元数据库）、Qdrant 向量库、Elasticsearch。
# 它本身几乎不干活，只负责三件事：找到配置文件、创建服务对象、用异步方式调用它。
# 脚本的入口
import asyncio   # 异步编程标准库（asyncio：让程序可以“同时等”多件事，而不是一件件排队）
from pathlib import Path   # pathlib 标准库里的 Path 类（用来方便地拼接、定位文件路径）

from app.service.meta_service import MetaService   # 导入服务类 MetaService（真正干活的业务层对象）


async def async_main():   # 定义异步主函数（用 async def 声明为异步，内部才能用 await）
    # 下面这个三引号是文档注释（说明函数用途），不是可执行代码
    '''
        初始化业务逻辑层对象
        调用业务逻辑层
    '''
    file_path = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'   # 拼出配置文件路径：__file__ 是本文件，parents[2] 往上退 3 层到项目根目录 Text2SQL1021，再进 conf 目录
    service = MetaService()   # 创建服务对象（此时什么都不会执行）
    await  service.build(file_path)   # 调用异步的 build() 方法，开始建库（await：在这里等它执行完）


# 下面这个三引号是模块级文档注释（说明整体入口），不是可执行代码
'''
程序入口
    因为代码使用异步编程
    所以main 方法需要使用asyncio.run 来调用异步方法
'''
if __name__ == '__main__':   # 只有“直接运行这个文件”时才为真；被别的文件 import 时不会执行下面这行
    asyncio.run(async_main())   # 启动事件循环，运行异步函数 async_main（asyncio.run 是异步程序的启动开关）