# ============================================================================
# 【文件说明】app/conf/app_config.py —— 项目配置的"模板类"（内层）
# 作用：规定 conf/app_config.yaml 里应该有哪些配置块、每块有哪些字段、字段是什么类型。
#       这里只画"格子"，不存具体值（IP、密码都在 YAML 里）。
# 怎么用：文件末尾调用 load_config()，把 YAML 里的真实值按字段名填进这些"格子"，
#       得到全局对象 appConfig；项目里通过 appConfig.db_meta.host 这样取值。
# 【注意】本文件用标准库 dataclasses 的 dataclass，而 app/conf/meta_config.py 用 pydantic 的
#         dataclass，两边风格不统一（都能跑，只是校验能力不同）。
# 【注意】dataclass（Python 自带的一种"纯装数据的盒子"写法：只声明字段名和类型，
#         自动生成初始化方法，不写业务逻辑）。
# ============================================================================
from dataclasses import dataclass  # 导入 dataclass 装饰器：把普通类变成"数据盒子"
from multiprocessing import context  # 【注意】导入了 context，但本文件从未使用，是没用的 import（不影响运行）
from pathlib import Path  # 导入 Path：用对象方式拼路径，不用手写字符串加斜杠

from omegaconf import OmegaConf  # 导入 OmegaConf（专门读写 YAML 配置的第三方库）；本文件只在下面被注释掉的旧代码里用到

from app.utils.load_config_util import load_config  # 导入自己写的加载函数：读 YAML → 按模板校验 → 转成对象


@dataclass  # 装饰器：让下面的类自动拥有构造方法（按字段顺序传值）
class BaseConfig:  # "主机+端口"型配置的公共父类，避免每个子类重复写 host/port
    host :str  # 主机地址（服务器 IP 或域名），字符串类型
    port :int  # 端口号（同一台服务器上不同服务用不同端口区分），整数类型

@dataclass  # 同样当数据盒子处理
class DBConfig(BaseConfig):  # MySQL 数据库配置：继承 BaseConfig，自动拥有 host、port
    user : str  # 登录数据库的用户名
    password : str  # 登录数据库的密码（【注意】YAML 里是明文）
    database :str  # 库名（一台 MySQL 服务器可以有多个库，靠库名区分）

@dataclass  # 同样当数据盒子处理
class QdrantConfig(BaseConfig):  # 向量库 Qdrant 的配置
    pass  # pass = 这里什么都不加；Qdrant 只需要 host+port，父类已经够了

@dataclass  # 同样当数据盒子处理
class EmbeddingConfig(BaseConfig):  # 向量化服务配置（把文字变成一串数字向量）
    embedding_size :int  # 向量维度：一条文本转成多少个数字（本项目 1024，必须与向量库集合的维度一致）

@dataclass  # 同样当数据盒子处理
class ESConfig(BaseConfig):  # ES（Elasticsearch，全文检索引擎）的配置
    pass  # ES 也只需要 host+port

@dataclass  # 同样当数据盒子处理
class LLMConfig:  # 大模型配置；它不连"主机+端口"，所以没继承 BaseConfig
    base_url:str  # 大模型接口的根地址（API 的网址前缀）
    api_key:str  # 调用大模型的密钥（相当于账号密码，【注意】YAML 里明文存放）
    model:str  # 具体使用的模型名

@dataclass  # 同样当数据盒子处理
class AppConfig:  # 总配置：把 6 个配置块组合成一个整体
    db_meta: DBConfig  # 元数据库（存"表/字段/指标的定义"，即描述数据的数据）
    db_dw: DBConfig  # 数仓库（真正存业务数据，最终生成的 SQL 在这里执行）
    qdrant: QdrantConfig  # 向量库（存文本向量，用于语义检索）
    embedding: EmbeddingConfig  # 向量化服务
    es: ESConfig  # 全文检索
    llm: LLMConfig  # 大模型

#加载配置文件，将配置文件的信息解析到appConfig对象中
# 【作用】算出配置文件的绝对路径：__file__ 是当前文件；parents[0]=conf、[1]=app、[2]=项目根目录
file_path= Path(__file__).parents[2] / 'conf' /'app_config.yaml'
# 下面 4 行是"被注释掉的旧写法"：手动 load → structured → merge，效果和 load_config() 一样，留作参考
# context = OmegaConf.load(file_path)
# schema = OmegaConf.structured(AppConfig)
#
# app_config = OmegaConf.to_object(OmegaConf.merge(schema, context))
# 【作用】真正加载：把 YAML 里的值按 AppConfig 的字段名逐层填进去，得到 appConfig 对象
appConfig: AppConfig = load_config(file_path,AppConfig)
# 注意： 配置文件属性名称一定要与class的属性名称一致，不然会导致数据无法正确加载

# 调试用：取消下面这行的注释即可打印全部配置（里面含明文密码，正式环境别打印）
# print(appConfig)
