from dataclasses import dataclass
from multiprocessing import context
from pathlib import Path

import load_config
from omegaconf import OmegaConf

@dataclass
class BaseConfig:
    host: str
    port: int

@dataclass
class DBConfig(BaseConfig):
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig(BaseConfig):
    pass

@dataclass
class EmbeddedConfig(BaseConfig):
    embedding_size: int

@dataclass
class ESConfig(BaseConfig):
    pass

@dataclass
class APPConfig(BaseConfig):
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedded: EmbeddedConfig
    es: ESConfig

#加载配置文件 , 将配置文件的信息解析到APPConfig对象中
file_path = Path(__file__).parent[2] / 'config'/'APP_config.yaml'
# context = OmegaConf.load(file_path)
# schema = OmegaConf.Structured(APPConfig)

APPconfig : APPConfig = load_config(file_path ,APPConfig)

print(APPconfig)
