from dataclasses import dataclass
from multiprocessing import context
from pathlib import Path

from omegaconf import OmegaConf


@dataclass
class BaseConfig:
    host :str
    port :int

@dataclass
class DBConfig(BaseConfig):
    user : str
    password : str
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

#加载配置文件，将配置文件的信息解析到appConfig对象中
file_path= Path(__file__).parents[2] / 'conf' /'app_config.yaml'
context = OmegaConf.load(file_path)
schema = OmegaConf.structured(AppConfig)

app_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
# 注意： 配置文件属性名称一定要与class的属性名称一致，不然会导致数据无法正确加载

print(app_config)
