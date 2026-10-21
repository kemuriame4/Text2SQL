from dataclasses import dataclass
from pathlib import Path
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
class EmbeddingConfig(BaseConfig):
    embedding_size:int

@dataclass
class ESConfig(BaseConfig):
    pass

@dataclass
class AppConfig:
    # 注意：配置文件的名字一定要与class中的属性名字一致
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig

# 加载配置文件，将配置文件的信息解析到appConfig对象中
file_path = Path(__file__).parents[2] / 'conf' / 'app_config.yaml'
# print(file_path)
# 加载文件内容
context = OmegaConf.load(file_path)
# 把数据加载到AppConfig对象里去 -- OmegaConf 自动映射
# 告知数据的结构
schema = OmegaConf.structured(AppConfig)
# 自动数据转换
app_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
print(app_config)