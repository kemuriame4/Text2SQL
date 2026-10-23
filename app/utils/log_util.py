from email.policy import default
import  os
from  loguru import  logger

from  contextvars import  ContextVar
from uuid import  uuid4
from  loguru import  logger
import  sys

from app.utils.log_util1 import write_log

_trace_id:ContextVar[str] = ContextVar("trace_id",default = "")

def trace_filter(record):
    """将上下文中的 trace_id 注入到每条日志记录中"""
    record["extra"]["trace_id"] = _trace_id.get() or "N/A"
    return  True

LOG_DIR = "../logs"
os.makedirs(LOG_DIR,exist_ok=True)

logger.remove()

logger.add(
    os.path.join(LOG_DIR,"app_{time:YYYY-MM-DD}.log"),
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
    diagnose=False,

)


def set_trace_id(trace_id: str = None):
    tid = trace_id or uuid4().hex
    _trace_id.set(tid)
    return tid

if __name__ == '__main__':
    set_trace_id()
    logger.info('这是第一条日志')
    write_log()