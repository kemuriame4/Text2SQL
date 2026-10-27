# ============================================================================
# 【文件说明】app/utils/load_config_util.py —— 配置加载小工具
# 作用：把 YAML 文件读进来，按"模板类"的字段名逐层合并 + 校验（检查有没有写错、有没有漏项），
#       最后转成普通 Python 对象返回。
# 三步原理：load（读 YAML）→ structured（把模板类变成结构模板）→ merge（按字段名合并并校验）。
# 谁用：app/conf/app_config.py（加载 app_config.yaml）、app/service/meta_service.py（加载 meta_config.yaml）。
# ============================================================================
from typing import Any  # 导入 Any：表示"任意类型"，class_name 参数可以传任何类

from omegaconf import OmegaConf  # 导入 OmegaConf 配置库（能读 YAML，也能按模板做类型约束）


def load_config(file_path:str, class_name: Any):  # 参数：YAML 文件路径 + 模板类；返回填好值的对象

    context = OmegaConf.load(file_path)  # 第一步：把 YAML 文件读成配置对象（这时还只是原始键值对）
    # 【作用】第二步：把模板类变成"结构模板"，规定好有哪些字段、每个字段什么类型
    schema = OmegaConf.structured(class_name)  # structured（把类转成带类型约束的结构）
    # 【作用】第三步：merge 按字段名把右边的具体值填进左边的模板；字段对不上/类型不对会报错
    config = OmegaConf.to_object(OmegaConf.merge(schema, context))  # to_object（把配置对象转成普通 Python 对象）
    return config  # 返回最终对象（例如 AppConfig 实例），调用方直接用属性取值