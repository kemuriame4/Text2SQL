# ============================================================================
# 【文件说明】app/utils/json_parser_util.py —— 解析数据库里 JSON 字段的小工具
# 作用：MySQL 中 alias（别名）、examples（示例值）这类列存的是 JSON 格式的字符串，
#       从数据库取出来后要转成 Python 的 list/dict（列表/字典）才能用；
#       这里负责转换，转不动就返回 None，不抛异常。
# 谁用：app/repository/mysql/column_info_mysql_repository.py
# 【注意】函数名前面的下划线 _ 是 Python 的约定，表示"模块内部使用"（不是强制限制）。
# ============================================================================
import json  # 导入标准库 json，用 json.loads 把 JSON 字符串变成 Python 对象
from typing import Any  # 导入 Any，表示参数和返回值可以是任意类型


def _parse_json_field(value: Any) -> Any:  # 参数 value 可以是 None/字符串/已是对象；返回解析结果或 None
    if value is None:  # 情况一：本来就是空值
        return None  # 没有东西可解析，直接返回 None
    if isinstance(value, str):  # 情况二：是字符串，才需要尝试解析；isinstance（判断值属于哪种类型的函数）
        try:  # 用 try 包住：解析失败也不会让整个程序崩溃
            return json.loads(value)  # json.loads（把 JSON 字符串转成 Python 的 dict 或 list）
        except json.JSONDecodeError:  # 捕获"这不是合法 JSON"的异常
            return None  # 或返回 []，看业务
    return value  # 情况三：不是字符串（已经是 dict/list 等），原样返回