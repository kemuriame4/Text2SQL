from loguru import logger

# logger.debug('debug')
# logger.info('info')
# logger.warning('warning')
# logger.error('error')

from contextvars import ContextVar
from uuid import uuid4
from loguru import logger
import sys

from app.utils.log_util1 import write_log

# 定义上下文变量
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")

def trace_filter(record):
    """将上下文中的 trace_id 注入到每条日志记录中"""
    record["extra"]["trace_id"] = _trace_id.get() or "N/A"
    return True

# 配置 Loguru 格式，包含 trace_id
# logger.remove()
# logger.add(
#     sys.stdout,
#     colorize=True,
#     format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
#            "<level>{level: <8}</level> | "
#            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
#            "<level>{message}</level>",
#     filter=trace_filter,
#     level='INFO'
# )

import os
from loguru import logger

LOG_DIR = "d:/logs"  # 或项目内的 logs/
os.makedirs(LOG_DIR, exist_ok=True)  # 确保目录存在

logger.remove()  # 清掉默认 stderr handler，避免重复

logger.add(
    os.path.join(LOG_DIR, "app_{time:YYYY-MM-DD}.log"),  # 按天分文件
    level="INFO",
    filter=trace_filter,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
           "trace={extra[trace_id]} | {name}:{line} | {message}",
    encoding="utf-8",        # 中文必须显式指定，否则 Windows 下默认 GBK
    colorize=False,          # 文件绝不能带颜色标签
    rotation="00:00",        # 每天零点切分新文件
    retention="30 days",     # 保留 30 天，过期自动删除
    compression="gz",        # 旧文件压缩为 .gz 节省磁盘
    enqueue=True,            # 多进程/多线程安全写入
    backtrace=True,          # 异常时显示完整回溯
    diagnose=False,          # 生产环境关掉变量值诊断，避免泄露敏感数据
)

# 在请求入口设置 ID（例如 FastAPI 中间件）
def set_trace_id(trace_id: str = None):
    tid = trace_id or uuid4().hex
    _trace_id.set(tid)
    return tid

if __name__ == '__main__':
    set_trace_id()
    logger.info('这是第一条日志')
    write_log()