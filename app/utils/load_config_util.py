"""配置加载工具：把 yaml 文件按 dataclass 结构解析成对象。"""
from typing import Any

from omegaconf import OmegaConf


def load_config(file_path:str, class_name: Any):
    """
    做什么：读一个 yaml 文件，按传入的 dataclass 结构做类型约束，返回实例化好的配置对象。
    参数：
    file_path (str)：yaml 文件的路径。
    class_name (Any)：一个 dataclass 类，例如 AppConfig、MetaConfig。
    返回：
    class_name 的实例，yaml 里的 key 会自动对到 dataclass 的同名字段。
    注意：yaml 里多出来的 key、或类型对不上的值，会在 merge 这一步直接抛异常。
    """

    context = OmegaConf.load(file_path)          # yaml 内容 → DictConfig
    schema = OmegaConf.structured(class_name)    # dataclass → 结构模板

    # merge：以 schema 为准，把 yaml 的值灌进去
    config = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return config



