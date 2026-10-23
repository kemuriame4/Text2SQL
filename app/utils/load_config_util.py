from omegaconf import OmegaConf


def load_config(config_path: str, schema: type | None = None):
    """加载 YAML 配置。

    传入 schema（dataclass）时会先构造结构化模板再做合并，
    从而获得类型校验与字段默认值填充能力。
    """
    config = OmegaConf.load(str(config_path))
    if schema is not None:
        config = OmegaConf.merge(OmegaConf.structured(schema), config)
    return OmegaConf.to_object(config)
