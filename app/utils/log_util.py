from pathlib import Path
from loguru import logger

# 创建日志目录
LOG_DIR = Path("../../logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 移除 Loguru 默认的控制台处理器，避免重复输出
logger.remove()

# 控制台输出
logger.add(
    sink=lambda message: print(message, end=""),
    level="INFO",  # DEBUG / INFO / WARNING / ERROR / CRITICAL
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# 普通日志文件：每天轮转，保留 30 天，并压缩旧日志
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - {message}"
    ),
    rotation="00:00",      # 每天午夜轮转；也可用 "100 MB"
    retention="30 days",   # 保留 30 天
    compression="zip",     # 也可用 "gz"
    encoding="utf-8",
    enqueue=True,          # 多线程/多进程场景下异步安全写入
    backtrace=True,
    diagnose=True,
)

# 错误日志单独记录
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    level="ERROR",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

# 使用示例
logger.debug("调试信息：变量值为 {}", 123)
logger.info("程序启动")
logger.warning("这是一个警告")
logger.error("发生错误")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("计算失败")  # 自动记录异常信息和堆栈