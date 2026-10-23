# Text2SQL1021 系统架构设计与解析文档

> 本文档针对 **Text2SQL1021** 项目进行系统性技术解析，使用 Mermaid 绘制完整的系统总体架构、代码工程分层、离线元数据沉淀、在线双路检索与智能体（Agent）状态流向图，并结合现有代码实现与演进规划进行详尽阐述。

---

## 1. 项目定位与核心设计理念

### 1.1 业务背景与解决痛点

在传统企业数据取数场景中，业务分析人员需要通过提工单、等待数据团队排期、反复沟通口径、编写 SQL、核对结果的漫长流程（通常以天为单位）。本项目旨在通过大语言模型（LLM）将自然语言问题（NL）自动化转写为**精准、安全、高性能、可解释**的 SQL 查询语句，实现“秒级自助取数”。

### 1.2 核心设计哲学：RAG + 知识库 + 智能体反思

传统的直接 Prompt 方式将整个数据库所有 Schema（DDL）灌给模型，在真实企业环境中存在以下致命缺陷：

1. **Token 限制与高昂成本**：大型数仓成百上千张表、上万字段，一次性输入超出上下文窗口且显著拉长首字响应时间（TTFT）。
2. **Schema 干扰与近义歧义**：无关表的相似字段（如 `pay_amount` vs `order_amount`、`create_time` vs `pay_time`）极易导致模型产生幻觉，发生 Schema Linking 错误。
3. **缺少动态统计特性与口径约束**：仅凭 DDL 无法获知字段枚举值、离散示例、外键连接路径及特定业务指标（如 GMV、AOV）的标准统计口径。

本项目采用 **“离线知识沉淀 + 在线双路混合检索（Schema Linking）+ LangGraph 循环自反思智能体 + 安全网关”** 的整体架构体系。

---

## 2. 总体系统架构图 (Overall System Architecture)

以下为系统的端到端总体架构，涵盖离线知识库构建体系、在线服务与编排层、检索层及执行安全网关：

```mermaid
flowchart TB
    %% 外部角色与交互
    USER(["业务分析师 / 用户终端"])

    %% 离线构建层
    subgraph OFFLINE["【离线层】元数据治理与知识库构建 Pipeline"]
        direction TB
        YAML_CFG["元数据与指标配置文件<br/>(meta_config.yaml)"]
        DW_SRC[("数据仓库 (DW MySQL)<br/>事实表/维度表业务数据")]

        META_EXTRACT["元数据解析与提取服务<br/>(MetaService / dw_mysql_repository)"]

        subgraph KB_STORES["多模态知识资产库 (Knowledge Base)"]
            DB_META[("元数据事实源 (MySQL)<br/>t_table_info / t_column_info<br/>t_metric_info / t_column_metric")]
            VEC_DB[("语义向量库 (Qdrant)<br/>列名/别名/注释多点向量表")]
            ES_DB[("全文倒排索引 (Elasticsearch)<br/>IK最细粒度中文分词与同义词")]
        end

        YAML_CFG --> META_EXTRACT
        DW_SRC -.->|"动态探测字段类型与枚举示例值"| META_EXTRACT
        META_EXTRACT -->|"结构化持久化"| DB_META
        META_EXTRACT -->|"文本嵌入 Embedding"| VEC_DB
        META_EXTRACT -->|"构建倒排索引"| ES_DB
    end

    %% 在线服务层
    subgraph ONLINE["【在线层】智能体编排与 RAG 检索管线"]
        direction TB
        NL_IN["自然语言输入 (Natural Language Query)"]

        subgraph REWRITE_MOD["意图理解与改写"]
            INTENT_PARSE["意图解析 / 实体提取 / 口径澄清"]
        end

        subgraph RETRIEVAL["Schema Linking 混合检索层"]
            direction LR
            VEC_SEARCH["Qdrant 向量语义检索<br/>(指标/口语/长描述召回)"]
            ES_SEARCH["ES BM25 关键词检索<br/>(表名/精确字段/编码召回)"]
            RRF_FUSION["RRF (Reciprocal Rank Fusion)<br/>倒数排名融合算法"]
            RERANK["Cross-Encoder 精排<br/>(Top-K 最优 Schema 截断)"]

            VEC_SEARCH --> RRF_FUSION
            ES_SEARCH --> RRF_FUSION
            RRF_FUSION --> RERANK
        end

        subgraph AGENT_LOOP["LangGraph 智能体状态机"]
            PROMPT_PACK["Prompt 上下文装配<br/>(DDL子集 + 枚举值 + 指标口径 + Few-Shot)"]
            LLM_GEN["LLM SQL 生成引擎<br/>(MiniMax / OpenAI GPT-4)"]
            VALIDATE{"SQL AST 静态语法<br/>与合规校验"}
            FIX_LOOP["错误反思与自修正回路<br/>(Reflection / Self-Correction)"]

            PROMPT_PACK --> LLM_GEN
            LLM_GEN --> VALIDATE
            VALIDATE --"校验失败 / 报错"--> FIX_LOOP
            FIX_LOOP --> LLM_GEN
        end

        NL_IN --> INTENT_PARSE
        INTENT_PARSE --> RETRIEVAL
        RETRIEVAL --> PROMPT_PACK
    end

    %% 安全执行与网关层
    subgraph GATEWAY["【安全治理网关】执行拦截与后验"]
        AST_CHECK["AST 白名单审计<br/>(只读限制: 禁用 DELETE/UPDATE/DROP)"]
        BUDGET_LIMIT["资源配额熔断<br/>(LIMIT 注入 / 最大超时 / 扫描行数阈值)"]
        DATA_MASK["数据脱敏与合理性校验<br/>(空结果核验 / 越界告警)"]
    end

    %% 数据仓库执行
    DW_QUERY[("数据仓库 (DW MySQL / StarRocks)<br/>只读账号受控连接池")]

    %% 连线
    USER -->|"输入业务问句"| NL_IN
    VEC_DB -.->|"语义召回"| VEC_SEARCH
    ES_DB -.->|"词法召回"| ES_SEARCH
    DB_META -.->|"主外键关系补充"| PROMPT_PACK

    VALIDATE --"校验通过"--> AST_CHECK
    AST_CHECK --> BUDGET_LIMIT
    BUDGET_LIMIT -->|"下推安全 SQL"| DW_QUERY
    DW_QUERY -->|"返回底层数据集"| DATA_MASK
    DATA_MASK -->|"生成图表/数据/引用解释"| USER

    classDef store fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef agent fill:#ede7f6,stroke:#512da8,stroke-width:2px;
    classDef safe fill:#ffebee,stroke:#d32f2f,stroke-width:2px;
    class DB_META,VEC_DB,ES_DB,DW_SRC,DW_QUERY store;
    class AGENT_LOOP,RETRIEVAL agent;
    class GATEWAY safe;
```

---

## 3. 代码工程分层与组件映射 (Component & DDD Layering)

本项目采用严格分层架构（清晰解耦数据实体、领域业务模型与基础设施接入），对应代码工程目录如下：

```mermaid
flowchart TD
    subgraph Presentation["入口与任务层 (Entrypoint & Scripts)"]
        M1["main.py (应用启动入口)"]
        M2["app/script/meta_init.py (元数据初始化批处理脚本)"]
    end

    subgraph ServiceLayer["业务逻辑层 (Service Layer)"]
        S1["app/service/meta_service.py (MetaService: 元数据解析、探测与同步调度)"]
    end

    subgraph DomainLayer["领域与实体层 (Entity & Mapper Layer)"]
        direction TB
        E1["app/entity/table_info_entity.py (TableInfoEntity)"]
        E2["app/entity/column_info_entity.py (ColumnInfoEntity)"]
        E3["app/entity/common_entity.py (CommonBaseEntity)"]

        MP1["app/mapper/table_info_mapper.py (TableInfoMapper)"]
        MP2["app/mapper/column_info_mapper.py (ColumnInfoMapper)"]

        E1 --- MP1
        E2 --- MP2
    end

    subgraph PersistenceLayer["持久化与仓储层 (Repository & Model Layer)"]
        direction TB
        R1["app/repository/mysql/table_info_mysql_repository.py"]
        R2["app/repository/mysql/column_info_mysql_repository.py"]
        R3["app/repository/mysql/dw/dw_mysql_repostory.py"]

        MD1["app/model/table_info_model.py (TableInfoModel - SQLAlchemy ORM)"]
        MD2["app/model/column_info_model.py (ColumnInfoModel - SQLAlchemy ORM)"]
        MD3["app/model/common_base.py (CommonBase 基类)"]

        R1 -.-> MD1
        R2 -.-> MD2
    end

    subgraph InfrastructureLayer["基础设施与客户端 (Client & Utils & Config)"]
        C1["app/client/mysql_client.py (CustomMySqlClient 异步连接池)"]
        CF1["app/conf/app_config.py & meta_config.py (配置定义)"]
        U1["app/utils/load_config_util.py (OmegaConf 动态加载器)"]
        U2["app/utils/log_util.py (Loguru 日志与全链路 TraceID 注入)"]
        YAML1["conf/app_config.yaml & conf/meta_config.yaml"]
    end

    %% 层级依赖流向
    Presentation --> ServiceLayer
    ServiceLayer --> DomainLayer
    ServiceLayer --> PersistenceLayer
    PersistenceLayer --> InfrastructureLayer
    DomainLayer --> InfrastructureLayer
    CF1 --> YAML1
```

### 各层级职责速查表

| 层级名称                      | 对应目录                    | 核心类/文件                                                                                                                                                                                                                                                                                                                                                                                                        | 核心职责                                                                 |
| ----------------------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| **配置层 (Config)**           | `conf/`, `app/conf/`        | [app_config.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/conf/app_config.py), [meta_config.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/conf/meta_config.py)                                                                                                                                                                                                                         | 强类型数据类校验系统级与元数据级 YAML 配置                               |
| **客户端层 (Client)**         | `app/client/`               | [mysql_client.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/client/mysql_client.py)                                                                                                                                                                                                                                                                                                                  | 基于 `asyncmy` + `SQLAlchemy` 异步引擎会话工厂管理                       |
| **仓储层 (Repository)**       | `app/repository/`           | [table_info_mysql_repository.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/repository/mysql/table_info_mysql_repository.py), [column_info_mysql_repository.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/repository/mysql/column_info_mysql_repository.py), [dw_mysql_repostory.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/repository/mysql/dw/dw_mysql_repostory.py) | 封装数据库 CRUD 操作、底层 DDL 反射及去重采样能力                        |
| **领域对象层 (Entity/Model)** | `app/entity/`, `app/model/` | [table_info_entity.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/entity/table_info_entity.py), [column_info_entity.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/entity/column_info_entity.py), [column_info_model.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/model/column_info_model.py)                                                                             | 区分业务 Domain Entity 与数据库映射 ORM Model                            |
| **实体转换层 (Mapper)**       | `app/mapper/`               | [table_info_mapper.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/mapper/table_info_mapper.py), [column_info_mapper.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/mapper/column_info_mapper.py)                                                                                                                                                                                         | 保证业务层代码不直接耦合底层 ORM 框架特性                                |
| **服务层 (Service)**          | `app/service/`              | [meta_service.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/service/meta_service.py)                                                                                                                                                                                                                                                                                                                 | 业务编排：加载配置、反查数仓字段类型、探查示例数据、执行 Upsert 批量入库 |
| **工具层 (Utils)**            | `app/utils/`                | [log_util.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/utils/log_util.py), [load_config_util.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/utils/load_config_util.py)                                                                                                                                                                                                                 | 异步 TraceID 注入、日志轮转与压缩、OmegaConf 模式反序列化                |

---

## 4. 离线元数据沉淀与同步时序图 (Offline Ingestion Pipeline)

系统通过 [meta_init.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/script/meta_init.py) 执行离线知识库构建，完整流程如下图所示：

```mermaid
sequenceDiagram
    autonumber
    participant Runner as 入口脚本 (meta_init.py)
    participant Service as 元数据服务 (MetaService)
    participant Config as 配置读取器 (load_config)
    participant DW_Repo as 数仓仓储 (DwMysqlRepostory)
    participant Meta_Repo as 元数据仓储 (Table/Column Info Repo)
    participant Meta_DB as 元数据库 (MySQL: meta_1022)
    participant DW_DB as 业务数仓 (MySQL: dw)

    Runner->>Service: 调用 build(file_path)
    Service->>Config: 解析 meta_config.yaml
    Config-->>Service: 返回 MetaConfig (tables, metrics)

    Service->>Service: 建立异步连接池 (CustomMySqlClient)

    loop 遍历每个 TableConfig
        Service->>Meta_Repo: get_table_info_by_id(table_name)
        Meta_Repo->>Meta_DB: SELECT * FROM t_table_info WHERE id = ?
        Meta_DB-->>Meta_Repo: 返回已存在记录或 None

        Service->>DW_Repo: get_column_type_by_name(table_name)
        DW_Repo->>DW_DB: SHOW COLUMNS FROM {table_name}
        DW_DB-->>DW_Repo: 返回物理数据类型映射字典

        loop 遍历当前表的每个 ColumnConfig
            Service->>DW_Repo: get_column_values(table_name, col_name, limit=5)
            DW_Repo->>DW_DB: SELECT DISTINCT {col} FROM {table} LIMIT 5
            DW_DB-->>DW_Repo: 返回真实数据样例 (Examples)

            Service->>Meta_Repo: get_column_info_by_id(column_id)
            Meta_Repo->>Meta_DB: SELECT * FROM t_column_info WHERE id = ?
            Meta_DB-->>Meta_Repo: 存在则入 update 队列，不存在入 add 队列
        end
    end

    Note over Service,Meta_DB: 开启事务执行批量持久化
    Service->>Meta_Repo: batch_update / batch_add (Tables & Columns)
    Meta_Repo->>Meta_DB: 批量执行 INSERT / UPDATE
    Meta_DB-->>Service: 事务提交成功
    Service-->>Runner: 返回已同步元数据字段列表
```

---

## 5. 多数据点语义向量设计 (Multi-Point Vector Indexing)

在 [README.md](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/README.md) 中提出的“多数据点”（Multi-Point）向量存储设计是解决中文自然语言同义词和多维度召回的关键：

```mermaid
flowchart LR
    subgraph COLUMN["物理字段: fact_order.order_amount"]
        NAME["字段名: order_amount"]
        DESC["字段描述: 订单金额"]
        ALIAS1["别名 1: 销售额"]
        ALIAS2["别名 2: 成交金额"]
        ALIAS3["别名 3: 收入"]
    end

    subgraph EMBEDDING["向量化处理 (1024 / 1536 维)"]
        V1["Vector Point 1"]
        V2["Vector Point 2"]
        V3["Vector Point 3"]
        V4["Vector Point 4"]
        V5["Vector Point 5"]
    end

    subgraph QDRANT["Qdrant 向量数据库存储点"]
        P1["Point ID: UUID-1<br/>Payload: {column_id: 'fact_order.order_amount', table: 'fact_order', role: 'measure'}"]
        P2["Point ID: UUID-2<br/>Payload: {column_id: 'fact_order.order_amount', table: 'fact_order', role: 'measure'}"]
        P3["Point ID: UUID-3<br/>Payload: {column_id: 'fact_order.order_amount', table: 'fact_order', role: 'measure'}"]
        P4["Point ID: UUID-4<br/>Payload: {column_id: 'fact_order.order_amount', table: 'fact_order', role: 'measure'}"]
        P5["Point ID: UUID-5<br/>Payload: {column_id: 'fact_order.order_amount', table: 'fact_order', role: 'measure'}"]
    end

    NAME --> V1 --> P1
    DESC --> V2 --> P2
    ALIAS1 --> V3 --> P3
    ALIAS2 --> V4 --> P4
    ALIAS3 --> V5 --> P5

    style COLUMN fill:#f1f8e9,stroke:#689f38
    style QDRANT fill:#e0f7fa,stroke:#0097a7
```

> **设计要点**：
>
> - 为什么不用 `column_id` 做 Point ID？因为一个字段对应多个向量点（名称、描述、N 个别名），若共用 ID 会相互覆盖，因此使用独立的 UUID 作为向量点主键。
> - Payload 均统一挂载完整的 `column_id`，召回时按 `column_id` 进行去重（Deduplication），保证在命中任一别名时都能准确拉出物理字段及宿主表信息。

---

## 6. 在线智能体工作流与反思状态图 (LangGraph State Graph)

在线生成采用 LangGraph 状态图模型构建反思修正循环，确保在生成 SQL 语法错误、执行超限或字段缺失时能够自我纠偏：

```mermaid
stateDiagram-v2
    [*] --> QueryAnalysis: 用户输入自然语言问句

    state QueryAnalysis {
        [*] --> ExtractEntities: 抽取实体、度量与时间范围
        ExtractEntities --> IntentRouting: 路由查询类型
    }

    QueryAnalysis --> SchemaLinking: 触发混合检索

    state SchemaLinking {
        [*] --> VectorSearch: Qdrant 向量召回 (Top 10)
        [*] --> KeywordSearch: ES IK分词检索 (Top 10)
        VectorSearch --> RRF: RRF 融合
        KeywordSearch --> RRF: RRF 融合
        RRF --> PruneTables: 根据指标/主外键拓扑补全关联表
    }

    SchemaLinking --> PromptAssembly: 生成精准上下文

    state PromptAssembly {
        [*] --> InjectDDL: 最小化相关表 DDL 拼装
        InjectDDL --> InjectSamples: 注入字段代表性取值 (Examples)
        InjectSamples --> InjectMetrics: 注入指标计算口径说明
        InjectMetrics --> InjectFewShot: 动态加载同构历史 SQL 样例
    }

    PromptAssembly --> SQLGeneration: 提交大模型生成

    state SQLGeneration {
        [*] --> LLMPredict: 产出结构化 SQL 文本
    }

    SQLGeneration --> ASTValidation: 进入语法与安全前检

    state ASTValidation {
        [*] --> ParseAST: sqlglot / AST 解析
        ParseAST --> ReadOnlyCheck: 阻断非 SELECT 语句
        ReadOnlyCheck --> ColumnExistenceCheck: 检查表名与字段存在性
    }

    ASTValidation --> SQLRepair: 校验失败 (语法/字段错)
    state SQLRepair {
        [*] --> FormatError: 提取具体解析报错
        FormatError --> RegenerateWithFeedback: 带上错误信息重新微调 Prompt
    }
    SQLRepair --> SQLGeneration: 重试 (最大重试上限 3 次)

    ASTValidation --> DryRunExecution: 校验通过，进入试跑执行

    state DryRunExecution {
        [*] --> InjectLimit: 强制注入 LIMIT 1000
        InjectLimit --> RunQuery: 只读连接池执行
    }

    DryRunExecution --> ExecutionErrorRepair: 数据库执行异常 (运行时错误)
    ExecutionErrorRepair --> SQLRepair: 转化为修正反馈

    DryRunExecution --> ResultInspection: 获得执行结果集

    state ResultInspection {
        [*] --> EmptyCheck: 结果为空检查 (时间边界/大小写)
        EmptyCheck --> FormatAnswer: 组合数据表格与图表推荐
    }

    ResultInspection --> [*]: 输出最终答案、SQL 语句及口径说明
```

---

## 7. 元数据数据库 ER 实体关系图 (Metadata Database Schema)

底层元数据库设计保证了**表、列、指标、关系**四个维度的完整追踪（依据 [initmysql](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/mysql/initmysql) 及 Model 实现）：

```mermaid
erDiagram
    t_table_info ||--o{ t_column_info : "1张表包含N个字段"
    t_column_info ||--o{ t_column_metric : "1个字段参与N个指标"
    t_metric_info ||--o{ t_column_metric : "1个指标关联N个字段"

    t_table_info {
        varchar(32) id PK "表名称 (如 fact_order)"
        varchar(64) name "表名"
        char(1) role "角色 (0:维度表, 1:事实表)"
        varchar(255) description "业务描述"
        char(1) del_flag "逻辑删除标记"
        datetime create_time "创建时间"
        datetime update_time "更新时间"
    }

    t_column_info {
        varchar(64) id PK "列全局唯一标识 (如 fact_order.order_amount)"
        varchar(128) name "列名称"
        varchar(64) type "物理数据类型 (varchar, decimal等)"
        varchar(32) role "列角色 (primary_key, foreign_key, measure, dimension)"
        json examples "真实数仓采样值列表"
        text description "列业务说明"
        json alias "同义词别名列表"
        varchar(64) table_id FK "所属表标识"
        char(1) del_flag "逻辑删除标记"
    }

    t_metric_info {
        varchar(64) id PK "指标编码 (如 GMV, AOV)"
        varchar(128) name "指标名称"
        text description "标准计算口径与业务定义"
        json relevant_columns "直接关联计算字段"
        json alias "指标别名"
        char(1) del_flag "逻辑删除标记"
    }

    t_column_metric {
        varchar(64) column_id PK,FK "字段ID"
        varchar(64) metric_id PK,FK "指标ID"
        char(1) del_flag "逻辑删除标记"
    }
```

---

## 8. 安全治理与执行防护网关 (Security Guard Architecture)

在企业级落地中，安全防御必须置于第一优先级，防护网关按流水线串行拦截：

```mermaid
flowchart TD
    RAW_SQL["待执行原始 SQL"] --> STEP1["① 静态 AST 解析检测 (SQLGlot)"]

    STEP1 --> Q1{"是否为只读 SELECT?"}
    Q1 --"否 (包含 INSERT/UPDATE/DELETE/DROP/ALTER)"--> BLOCK1["拦截: 抛出安全越权异常"]

    Q1 --"是"--> STEP2["② 危险操作扫描"]
    STEP2 --> Q2{"是否存在 SELECT * 无限定全表扫描?"}
    Q2 --"是"--> REWRITE1["自动按 Schema 改写为指定字段并注入 LIMIT 1000"]
    Q2 --"否"--> STEP3
    REWRITE1 --> STEP3["③ 资源消耗预算审计 (Resource Budget)"]

    STEP3 --> Q3{"JOIN 深度 <= 3 且预计耗时预算受控?"}
    Q3 --"超标 (笛卡尔积/无索引关联)"--> BLOCK2["拦截: 要求用户收敛查询范围"]

    Q3 --"合规"--> STEP4["④ 执行器路由 (只读连接池)"]
    STEP4 --> EXEC["执行于只读副本，配置 Socket Timeout (e.g. 5000ms)"]

    EXEC --> STEP5["⑤ 数据脱敏输出 (Masking)"]
    STEP5 --> SAFE_OUTPUT["向用户返回受控安全数据与可视化分析"]

    style BLOCK1 fill:#ffcdd2,stroke:#c62828
    style BLOCK2 fill:#ffcdd2,stroke:#c62828
    style SAFE_OUTPUT fill:#c8e6c9,stroke:#2e7d32
```

---

## 9. 模块映射与当前工程现状总结

### 9.1 当前已落地模块

1. **统一异步数据库基础设施**：[mysql_client.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/client/mysql_client.py) 实现了基于 `SQLAlchemy` + `asyncmy` 的异步会话池管理器。
2. **元数据自动反射与探测引擎**：[meta_service.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/service/meta_service.py) 实现了读取业务 YAML，自动探查 DW 数据仓库对应表的字段类型与去重数据样本，并执行差异化 Upsert 写入元数据库。
3. **分层清晰的领域模型与映射器**：Entity、Model、Mapper、Repository 层各司其职，保证了业务层与 ORM/SQL 的解耦。
4. **全链路可追踪日志**：[log_util.py](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/utils/log_util.py) 具备 ContextVar 驱动的异步 `trace_id` 自动注入与滚动压缩存储。

### 9.2 规划演进方向

- **在线检索层落地**：完善 Qdrant 向量写入脚本与混合检索路由（Vector + BM25）。
- **LangGraph 智能体状态图构建**：实现生成、校验、重试三节点的闭环编排。
- **FastAPI 对外接口暴露**：封装统一的问答与数据可视化 API。

# 针对您的两个问题，下面从**“自然语言全生命周期流转流程”**与**“系统组件部署架构拓扑（同机 vs 分布式）”**两个维度为您做深度解析：

---

### 一、 客户输入自然语言后的端到端全流程流转

当业务人员在前端输入自然语言（例如：_“查询上季度华东大区各品类的成交总额前5”_）后，系统内部经历 **7 个核心阶段**，完整流转时序如下图所示：

```mermaid
sequenceDiagram
    autonumber
    actor User as 业务人员 / 前端UI
    participant API as Web网关/FastAPI (设置TraceID)
    participant Agent as LangGraph 智能体中枢
    participant Router as 意图与实体解析模块
    participant Hybrid as 双路检索 (Qdrant + ES)
    participant MetaDB as 元数据库 (t_table/column_info)
    participant LLM as 大语言模型 (MiniMax/GPT-4)
    participant Guard as AST 安全与限额网关
    participant DW as 业务数仓 (DW 只读库)

    User->>API: 提交提问: "查询上季度华东大区各品类成交总额前5"
    API->>API: 注入全链路 trace_id (log_util.py)
    API->>Agent: 启动工作流状态机

    %% 1. 意图解析
    Agent->>Router: 解析意图、时间、度量与维度
    Router-->>Agent: 提取: 指标=成交总额(GMV), 维度=品类/大区, 过滤=华东, 时间=上季度

    %% 2. 混合检索 Schema Linking
    Agent->>Hybrid: 并发检索相关字段与指标
    par 语义向量召回
        Hybrid->>Hybrid: Qdrant 检索: "成交总额" -> fact_order.order_amount / GMV
    and 关键词倒排召回
        Hybrid->>Hybrid: ES BM25 检索: "品类" -> dim_product.category, "华东" -> dim_region
    end
    Hybrid-->>Agent: RRF 融合去重，命中表: fact_order, dim_product, dim_region, dim_date

    %% 3. 上下文富化
    Agent->>MetaDB: 补全主外键拓扑与字段真实采样值 (Examples)
    MetaDB-->>Agent: 补充: 关联字段/枚举示例(如: '华东', '华南')/口径公式

    %% 4. 生成与自修正循环
    Agent->>LLM: 组装 Prompt (精简DDL + 样本 + 指标定义) -> 请求生成 SQL
    LLM-->>Agent: 返回生成的 SQL 语句

    Agent->>Guard: 进行静态 AST 语法解析与白名单安全审计
    alt 校验不通过 (语法错误 / 引用了非白名单字段)
        Guard-->>Agent: 拦截并捕获具体语法/表字段错误
        Agent->>LLM: 携带错误信息反思重试 (Self-Correction Loop, 最多3次)
    else 校验通过
        Guard->>Guard: 强制注入 LIMIT 1000 与超时截断保护
        Guard->>DW: 使用只读账号下推受控 SQL
        DW-->>Guard: 返回实际执行数据集 (Rows)
        Guard-->>Agent: 返回清洗后的纯只读安全数据
    end

    %% 5. 组装结果交付
    Agent->>Agent: 数据合理性审查 (空值核验 / 越界告警)
    Agent-->>API: 组合结构化数据 + 生成的SQL + 口径引用来源
    API-->>User: 渲染呈现最终数据表格 / 统计图表 / 解释说明
```

#### 流程详细分解：

1. **网关接入与链路追踪**：
   - 请求进入后，[`log_util.py`](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/app/utils/log_util.py#L60-L65) 自动为该次请求生成全局唯一 `trace_id` 并挂载到异步上下文，确保后续所有的检索、模型交互、数据库查询日志均可全链路复盘。
2. **意图解析与时间规整**：
   - 提取实体与口径：识别出时间概念（“上季度”依据当前时间换算为绝对日期边界 `2026-04-01 ~ 2026-07-01`，避免模型直接写易错的动态函数）、指标（“成交总额”对应元数据配置中的 `GMV`）、维度（“华东大区”、“品类”）。
3. **双路混合检索（Schema Linking）**：
   - **Qdrant 向量路**：针对业务自然语言、行业同义词进行向量余弦相似度匹配，召回相关字段与指标。
   - **ES 关键词路**：通过 IK 中文分词进行精确表名、字段英文名、精确别名的 BM25 检索。
   - **拓扑关系补全**：利用元数据库中已沉淀的 `t_column_info` 主外键定义，自动补齐这几张维度表与事实表之间的关联路径（JOIN ON 键）。
4. **动态 Prompt 上下文装配**：
   - 杜绝塞入数仓全部表结构，仅装配本次召回的 **4 张表**的精简 DDL，并附带离线阶段探测好的真实采样值（`examples`，例如明确告诉模型字段值是 `'华东'` 而不是 `'华东大区'`，防止 `WHERE` 过滤命中空值）。
5. **AST 静态安全审计与自反思修正回路**：
   - 大模型生成 SQL 后，先经过 AST 解析：**绝对拦截 `INSERT/UPDATE/DELETE/DROP`**，严检字段合法性；
   - 若出现字段名写错或函数报错，智能体不会直接抛错给用户，而是把错误信息回填给大模型触发 **Self-Correction 重新修正生成**（最大重试 3 次）。
6. **受控执行与结果呈现**：
   - 强制补充 `LIMIT 1000` 并设置 Socket 查询超时，在只读连接池中执行，最终将数据结果集、执行的 SQL 以及口径解释一同返回给用户。

---

### 二、 各部分后续部署在同一服务器还是不同？

**结论：开发测试阶段建议“单机多容器轻量部署”，生产正式环境强烈建议“分布式多节点独立部署”。**

在项目配置文件 [app_config.yaml](file:///c:/Users/admin/PycharmProjects/Text2SQL1021/conf/app_config.yaml) 中可以看到，当前阶段开发环境将 `db_meta`、`db_dw`、`qdrant`、`embedding`、`es` 统一指向了单机 IP `172.16.50.95`。后续演进考量如下：

#### 1. 各组件资源画像与瓶颈分析

| 组件分类         | 包含模块                                 | 资源特性                                                         | 为何生产不能混布在同一台机                                           |
| ---------------- | ---------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| **应用计算层**   | FastAPI / LangGraph 智能体 / MetaService | **CPU/网络 I/O 密集型**，无状态 (Stateless)                      | 需要随业务并发请求动态弹性伸缩，不能被底层存储的毛刺影响             |
| **向量检索层**   | Qdrant                                   | **内存/CPU 密集型** (HNSW 向量索引常驻内存)                      | 高并发向量计算打满 CPU 时，会直接拖垮同主机的应用进程                |
| **全文检索层**   | Elasticsearch                            | **JVM 堆内存/磁盘 I/O 密集型** (极度吃内存，通常需 8G~32G+)      | 触发 JVM Full GC 或高 I/O 读写时可能导致宿主机整体响应变慢甚至 OOM   |
| **元数据库**     | MySQL (`meta_1022`)                      | 轻量级关系型数据，数据量小（千行级）                             | 读多写极少，可使用企业既有的公共 MySQL 实例或轻量实例                |
| **核心业务数仓** | 业务 DW (MySQL/StarRocks 等)             | **磁盘 I/O/内存/吞吐核心**                                       | **企业核心资产，网络必须物理或逻辑隔离**，绝对禁止与外围检索应用混布 |
| **模型推理服务** | MiniMax / DeepSeek / 本地 BGE Embedding  | 若使用云端 API 则零本地开销；若私有化部署则为 **GPU 显存密集型** | 本地推理必须配备专用 GPU 计算卡（如 A10/4090），普通服务器无法运行   |

---

#### 2. 生产环境推荐部署拓扑图

生产落地时推荐采用 **分层解耦拓扑**：

```mermaid
flowchart TD
    subgraph INGRESS["接入与负载均衡层"]
        LB["Nginx / 云负载均衡 SLB"]
    end

    subgraph APP_NODES["应用计算集群 (无状态，K8s Pods / 容器集群)"]
        APP1["FastAPI + Agent 节点 1"]
        APP2["FastAPI + Agent 节点 2"]
    end

    subgraph RETRIEVAL_CLUSTER["知识检索集群 (独立部署/云托管)"]
        QDRANT[("Qdrant 向量服务<br/>(专用内存优化型节点)")]
        ES[("Elasticsearch 检索集群<br/>(专用大内存/高SSD节点)")]
    end

    subgraph RDBMS_CLUSTER["关系与元数据库 (云 RDS / 共享数据库)"]
        META_DB[("MySQL 元数据库<br/>(存储表/列/指标配置)")]
    end

    subgraph DW_ZONE["企业数据安全核心隔离区 (数仓网段)"]
        DW[("DW 数据仓库 / 业务分析库<br/>(配置严格只读账号 + 网络白名单)")]
    end

    subgraph AI_SERVICES["大模型推理能力"]
        CLOUD_LLM["云端大模型 API<br/>(MiniMax / OpenAI)"]
        LOCAL_EMB["Embedding 推理服务<br/>(GPU节点或轻量模型容器)"]
    end

    LB --> APP1
    LB --> APP2

    APP1 & APP2 --> QDRANT
    APP1 & APP2 --> ES
    APP1 & APP2 --> META_DB
    APP1 & APP2 --> LOCAL_EMB
    APP1 & APP2 -.->|"公网/专线 HTTPS"| CLOUD_LLM

    APP1 & APP2 ==>|"只读内网访问 (受限端口/白名单)"| DW

    classDef app fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef store fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef secure fill:#ffebee,stroke:#d32f2f,stroke-width:2px;
    class APP1,APP2 app;
    class QDRANT,ES,META_DB,LOCAL_EMB store;
    class DW secure;
```

---

#### 3. 阶段化落地演进建议

1. **开发联调 / POC 阶段（当前阶段）**：
   - **部署形式**：**单台高性能机器（16核32G以上）** 或 **局域网共用机器**（如目前的 `172.16.50.95`）。
   - **管理方式**：使用 `Docker Compose` 一键拉起 MySQL、Qdrant、ES 容器；Python 代码在本地开发环境直接运行。优势是环境成本低、网络延迟小、联调排错速度快。
2. **生产上线阶段（正式运行）**：
   - **应用服务（FastAPI/Agent）**：打包为轻量 Docker 镜像，部署在 Kubernetes (K8s) 或无状态轻量服务器上，方便依据业务访问量弹性扩展副本；
   - **Qdrant 与 ES**：使用独立的存储服务器或直接采购公有云托管服务（如 AWS/阿里云 ES、Qdrant Cloud），规避内存溢出互踩崩溃；
   - **DW 数据仓库**：沿用企业现有的分析型数据库/只读从库，通过防火墙仅对应用层节点开放 3306/查询端口，并严格下发**只读账号权限**。
