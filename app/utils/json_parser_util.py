import json
from typing import Any


def _parse_json_field(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None  # 或返回 []，看业务
    return value