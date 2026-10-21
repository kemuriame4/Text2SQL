from dataclasses import dataclass
from pathlib import Path
from omegaconf import OmegaConf

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
print(file_path)
config = OmegaConf.load(str(file_path))
schema = OmegaConf.structured(config)
app_config = OmegaConf.to_object(OmegaConf.merge(config, schema))
print(app_config)
