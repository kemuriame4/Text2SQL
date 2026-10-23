from typing import Any

from omegaconf import OmegaConf


def load_config(file_path: str, config_class:Any):
    """
    加载配置文件
    :param file_path: 配置文件路径
    :param config_class: 配置类
    :return: 配置对象
    """
    context = OmegaConf.load(file_path)
    schema = OmegaConf.structured(config_class)
    config = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return config