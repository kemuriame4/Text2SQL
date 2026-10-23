

from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

from app.utils.load_config_util import load_config


@dataclass
class BaseConfig:
    host :str
    port :str

@dataclass
class DBConfig(BaseConfig):
    user :str
    password :str
    database :str

@dataclass
class QdrantConfig(BaseConfig):
    pass

@dataclass
class EmbeddingConfig(BaseConfig):
    embedding_size :int

@dataclass
class ESConfig(BaseConfig):
    pass

@dataclass
class AppConfig:
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig

file_path = Path(__file__).parents[2] / 'conf' / 'app_config.yaml'

appConfig = load_config(file_path, AppConfig)