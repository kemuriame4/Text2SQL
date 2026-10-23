"""应用级配置：把 conf/app_config.yaml 解析成 AppConfig 对象，供全局使用。"""
from dataclasses import dataclass
from multiprocessing import context
from pathlib import Path

from omegaconf import OmegaConf

from app.utils.load_config_util import load_config


@dataclass
class BaseConfig:
    """所有连接类配置的公共部分（主机 + 端口）。"""
    # 字段：
    # host (str)：服务主机 IP 或域名。
    # port (int)：服务端口。
    host :str
    port :int

@dataclass
class DBConfig(BaseConfig):
    """MySQL 连接配置，继承 host / port。"""
    # 字段：
    # host (str)：数据库主机，见 yaml 中 db_meta / db_dw。
    # port (int)：端口，默认 3306。
    # user (str)：登录用户名。
    # password (str)：登录密码。
    # database (str)：库名，元数据库和数据仓库是两个不同的库。
    user : str
    password : str
    database :str

@dataclass
class QdrantConfig(BaseConfig):
    """Qdrant 向量库连接配置，只用 host / port。"""
    pass

@dataclass
class EmbeddingConfig(BaseConfig):
    """向量化服务配置，比 Qdrant 多一个向量维度。"""
    # 字段：
    # host (str)：向量化服务主机。
    # port (int)：向量化服务端口。
    # embedding_size (int)：向量维度，必须和 Qdrant collection 的维度一致。
    embedding_size :int

@dataclass
class ESConfig(BaseConfig):
    """Elasticsearch 连接配置，只用 host / port。"""
    pass


@dataclass
class AppConfig:
    """整份 app_config.yaml 的结构，字段名必须和 yaml 顶层 key 完全一致。"""
    # 字段：
    # db_meta (DBConfig)：元数据库（存表/字段/指标元数据）。
    # db_dw (DBConfig)：数据仓库（存真实的维度表和事实表）。
    # qdrant (QdrantConfig)：向量库。
    # embedding (EmbeddingConfig)：向量化服务。
    # es (ESConfig)：Elasticsearch。
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig

#加载配置文件，将配置文件的信息解析到appConfig对象中
file_path= Path(__file__).parents[2] / 'conf' /'app_config.yaml'
# context = OmegaConf.load(file_path)
# schema = OmegaConf.structured(AppConfig)
#
# app_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
# 模块导入时立刻执行一次，所以 appConfig 是全局唯一的配置实例
appConfig: AppConfig = load_config(file_path,AppConfig)
# 注意： 配置文件属性名称一定要与class的属性名称一致，不然会导致数据无法正确加载

# print(appConfig)
