"""日志辅助模块：演示跨模块调用时 loguru 的 logger 是同一个实例。"""
from loguru import logger


def write_log():
    """
    做什么：打一条 error 级别的日志，内容固定为"调用write_log"。
    参数：无。
    返回：None。
    注意：这里没有独立配置 logger，用的是 log_util 里已经 add 好的那些 handler，
    所以日志会写进同一个文件；如果没有先 import log_util，则走 loguru 的默认输出（控制台）。
    """
    logger.error('调用write_log')
