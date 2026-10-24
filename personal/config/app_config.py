from omegaconf import OmegaConf
from sys import argv
from pathlib import Path
from dataclasses import dataclass


@dataclass
class BaseConfig:
    host: str
    port: int


@dataclass
class DatabaseConfig(BaseConfig):
    user: str
    password: str
    database: str


@dataclass
class QdrantConfig(BaseConfig):
    pass


@dataclass
class EmbeddingConfig(BaseConfig):
    embedding_size: int


@dataclass
class ESConfig(BaseConfig):
    pass


@dataclass
class AppConfig:
    """总配置类，包含所有配置信息。"""

    database_meta: DatabaseConfig
    database_dw: DatabaseConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig


if "--personal" in argv:
    file_path = Path("personal_config.yaml")
else:
    file_path = Path("app_config.yaml")

context = OmegaConf.load(file_path)
schema = OmegaConf.structured(AppConfig)

app_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
