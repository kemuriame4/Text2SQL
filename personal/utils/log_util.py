from uuid import uuid4
from loguru import logger
from contextvars import ContextVar
import os

LOG_DIR = "./../logs"
os.makedirs(LOG_DIR, exist_ok=True)
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")


def trace_filter(record):
    record["extra"]["trace_id"] = _trace_id.get() or "N/A"
    return True


logger.remove()

logger.add(
    os.path.join(LOG_DIR, "app_{time:YYYY-MM-DD}.log"),  # 按天分文件
    level="INFO",
    filter=trace_filter,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "trace={extra[trace_id]} | {name}:{line} | {message}",
    encoding="utf-8",  # 中文必须显式指定，否则 Windows 下默认 GBK
    colorize=False,  # 文件绝不能带颜色标签
    rotation="00:00",  # 每天零点切分新文件
    retention="30 days",  # 保留 30 天，过期自动删除
    compression="gz",  # 旧文件压缩为 .gz 节省磁盘
    enqueue=True,  # 多进程/多线程安全写入
    backtrace=True,  # 异常时显示完整回溯
    diagnose=False,  # 生产环境关掉变量值诊断，避免泄露敏感数据
)


def set_trace_id(trace_id: str = None):
    """设置 trace_id"""
    tid = trace_id if trace_id is not None else uuid4().hex
    _trace_id.set(tid)
    return tid
