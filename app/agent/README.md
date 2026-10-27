智能体工作流开发
    分词节点：采用的是jieba分词，根据词性进行分词，分词之后的结果转换为list，将分词后的keywords写入state中
    字段召回：
        根据用户的问题，进行字段扩词（使用大模型扩词），将原来分词的关键词与扩词的关键词合并；
        循环关键词，将关键词向量化，在qdrant中进行语义相似度检索；检索的结果存储到字典中（使用字典进行数据去重）
        将数据转换为list并且写入到state中
    指标召回
        根据用户的问题，进行指标扩词（使用大模型扩词），将原来分词的关键词与扩词的关键词合并；
        循环关键词，将关键词向量化，在qdrant中进行语义相似度检索；检索的结果存储到字典中（使用字典进行数据去重）
        将数据转换为list并且写入到state中
    取值召回
        根据用户的问题，进行取值扩词（使用大模型扩词），将原来分词的关键词与扩词的关键词合并；
        循环关键词，在ES中进行文本相似度的匹配；检索的结果存储到字典中（使用字典进行数据去重）
        将数据转换为list并且写入到state中
    合并
        将多路召回的数据从state取出
        将字段信息列表转换为字典（key：字段id，值字段信息对象ColumnInfoEntity）；column_map
        循环指标信息，获取到指标信息中的关联字段
            循环关联字段，判断字段是否在字典（column_map）中，
                如果不存在，根据字段id查询字段的完整信息，并且添加到字典中
        循环取值信息
            判断取值信息是否在字典（column_map）中
                如果不存在，根据字段id查询字段的完整信息，并且添加到字典中
            设置字段的examples的值     
        创建表字典table_map
        根据表id进行分组
            循环字段字典，获取字段对象
                如果表id，不在table_map中
                    将table_id 添加到字典中
                将字段信息添加到对应的table_id下
        循环table_map 字典
            根据表id获取表的主外键信息，并且添加到对应table_id下
        组装state数据
            组装表的状态数据
            组装指标的状态数据
        将两个状态数据返回
比如：
    字段召回的是：dim_region.region_name
    指标召回的是：fact_order.order_amount
    取值召回的是：dim_date.quarter
        将三路召回的所有的字段信息进行完善
            {
                'dim_region.region_name': ColumnInfoEntity,
                'fact_order.order_amount': ColumnInfoEntity,
                'dim_date.quarter': ColumnInfoEntity,
            }
        将字段信息根据表id进行分组
            {
                'fact_order':[ColumnInfoEntity],
                'dim_region':[ColumnInfoEntity],
                'dim_date':[ColumnInfoEntity],
            }
        完善每一个表的主外键信息
            {
                'fact_order':[ColumnInfoEntity,FK ColumnInfoEntity,PK ColumnInfoEntity],
                'dim_region':[ColumnInfoEntity,FK ColumnInfoEntity,PK ColumnInfoEntity],
                'dim_date':[ColumnInfoEntity,FK ColumnInfoEntity,PK ColumnInfoEntity],
            }
        组装state数据结构  TableInfoState
            [
                TableInfoState(
                    name,
                    description,
                    role,
                    alias,
                    columns:[ColumnInfoState]
                )   
            ] 
表信息过滤：
    拿到TableInfoState数据
    使用大模型剔除无关的数据
    大模型返回需要保留的表信息和字段信息
    进行数据的处理
    返回


        

            

            

        

    