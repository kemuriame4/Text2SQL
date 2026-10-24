app/api：对外暴露的接口层
app/client：连接 MySQL、Qdrant、Elasticsearch、Embedding 模型的客户端层
app/conf：配置文件读取与解析层
app/entity：业务领域实体层
app/mapper：业务实体（Entity）与数据模型（Model）的转换工具层
app/model：数据库 ORM 实体层
app/repository：数据访问与仓储交互层
app/script：离线初始化与批处理脚本
app/service：核心业务逻辑编排层
app/utils：通用工具函数库
