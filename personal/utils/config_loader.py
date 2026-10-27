from omegaconf import OmegaConf
from typing import Any


def load_config(file_path: str, class_name: Any):
    context = OmegaConf.load(file_path)
    schema = OmegaConf.structured(class_name)
    config = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return config
