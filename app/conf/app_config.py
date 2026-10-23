from dataclasses import dataclass
from multiprocessing import context
from pathlib import Path

@dataclass
class BaseConfig:
    host:str
    port:int

@dataclass
class DBConfig(BaseConfig):
    user:str
    password:str
    database:str

@dataclass
class QdrantConfig(BaseConfig):
    pass

@dataclass
class EmbeddingConfig(BaseConfig):
    embedding_size:int

@dataclass
class ESConfig(BaseConfig):
    pass

@dataclass
class AppConfig:
    db_meta:DBConfig
    db_dw:DBConfig
    qdrant:QdrantConfig
    embeddign:EmbeddingConfig
    es:ESconfig