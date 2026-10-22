

from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf


@dataclass
class BaseConfig:
    host :str
    port :str

@dataclass
class DBConfig(BaseConfig):
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

context = OmegaConf.load(file_path)

schema = OmegaConf.structured(AppConfig)

app_config = OmegaConf.to_object(OmegaConf.merge(context,schema))

print(app_config)