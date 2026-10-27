# ============================================================================
# 【文件说明】app/utils/log_util.py —— 日志工具
# 作用：统一配置 loguru（第三方日志库），把日志写到文件：按天切分、保留 30 天、旧文件自动压缩；
#       每条日志自动带上 trace_id（一次请求的追踪号，查问题时靠它把同一次请求的日志串起来）。
# 怎么用：其他模块直接 import logger 使用；请求入口先调用 set_trace_id() 生成追踪号。
# 【注意】日志目录写死为 d:/logs（Windows 盘符路径），换到 Linux 服务器会直接失败。
# ============================================================================
from loguru import logger  # 导入 loguru 的 logger（全局单例，直接调用 info/error 等方法写日志）

# 下面是 loguru 各种级别的用法示例（已注释，仅作备忘）
# logger.debug('debug')
# logger.info('info')
# logger.warning('warning')
# logger.error('error')

from contextvars import ContextVar  # 导入 ContextVar：标准库的"上下文变量"，用来存 trace_id
from uuid import uuid4  # 导入 uuid4：生成随机且几乎不会重复的 ID

import sys  # 导入 sys；【注意】当前代码只在被注释掉的旧配置里用到它，实际用不到

from app.utils.log_util1 import write_log  # 导入同目录 log_util1 里的 write_log（只在下面测试代码里用）

# 定义上下文变量
# 【作用】ContextVar（上下文变量）：同一个请求/线程里，各个函数都能读到同一个 trace_id，不会串号
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")  # 类型是"字符串的上下文变量"，默认空值

def trace_filter(record):  # 日志过滤器：loguru 每写一条日志都会先调用它
    """将上下文中的 trace_id 注入到每条日志记录中"""
    # record（日志记录，本质是个字典）：装着这条日志的时间、级别、消息等字段
    record["extra"]["trace_id"] = _trace_id.get() or "N/A"  # 往附加字段 extra 里塞 trace_id；取不到就写 N/A
    return True  # 必须返回 True，这条日志才会被真正输出

# 配置 Loguru 格式，包含 trace_id
# 下面这一段是"输出到控制台"的旧配置（整段被注释掉）：现在只写文件，保留作参考
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

import os  # 导入 os：用来创建目录、拼文件路径
from loguru import logger  # 【注意】重复导入：第 1 行已经导入过，这行是多余的（无害）

# 【注意】日志目录写死成 d:/logs（Windows 盘符路径），换机器/换系统会直接失败
LOG_DIR = "d:/logs"  # 或项目内的 logs/
os.makedirs(LOG_DIR, exist_ok=True)  # 确保目录存在

logger.remove()  # 清掉默认 stderr handler，避免重复
# handler（处理器）指"日志的输出目标"；先移除默认的屏幕输出，避免同一条日志打印两遍

# 【作用】添加一个输出目标：按天生成日志文件
logger.add(
    os.path.join(LOG_DIR, "app_{time:YYYY-MM-DD}.log"),  # 按天分文件
    level="INFO",  # 只记录 INFO 及以上级别（debug 不记）
    filter=trace_filter,  # 每条日志先过过滤器，把 trace_id 塞进 extra 字段
    # 日志格式：时间 | 级别 | trace_id（追踪号） | 代码位置（模块:行号） | 消息
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
def set_trace_id(trace_id: str = None):  # 给当前请求设置 trace_id；不传就自动生成一个
    tid = trace_id or uuid4().hex  # 没传值就用 uuid4().hex 生成 32 位随机十六进制串
    _trace_id.set(tid)  # 把 trace_id 存进当前上下文，同一请求内各函数都能读到
    return tid  # 返回出去，方便调用方打印或继续传递

if __name__ == '__main__':  # 只有"直接运行本文件"时才执行下面三行（被 import 时不执行），仅用于测试
    set_trace_id()  # 生成一个 trace_id
    logger.info('这是第一条日志')  # 写一条 INFO 日志，验证文件里能正常落盘
    write_log()  # 调用 log_util1 的函数，验证跨文件写日志也带 trace_id