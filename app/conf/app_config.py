from dataclasses import dataclass
from pathlib import Path
from omegaconf import OmegaConf

from app.utils.load_config_util import load_config


@dataclass
class BaseConfig:
    host: str
    port: int


@dataclass
class DbConfig(BaseConfig):
    username: str
    password: str
    database: str


@dataclass
class QdrantConfig(BaseConfig):
    pass


@dataclass
class EsConfig(BaseConfig):
    pass


@dataclass
class EmbeddingConfig(BaseConfig):
    embedding_size: int

@dataclass
class AppConfig:
    db_dw: DbConfig
    db_meta: DbConfig
    es: EsConfig
    embedding: EmbeddingConfig
    qdrant: QdrantConfig

file_path = Path(__file__).parents[2]/'conf'/'app_config.yaml'
app_config: AppConfig = load_config(str(file_path))
print(app_config)
