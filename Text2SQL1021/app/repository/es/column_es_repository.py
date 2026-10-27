# 【文件作用】
# 这个文件负责把"字段的具体取值"写进 / 读出自 Elasticsearch（ES，全文搜索引擎，按关键词做分词匹配）。
# 属于 repository 层（数据读写层），往上被 service 或 agent 节点调用。
# 典型用途：用户提到"华东""华南"这类具体值时，去 ES 里搜出它属于哪个字段。

from dataclasses import asdict  # 导入 asdict：把 dataclass 对象一键转成普通字典

from elasticsearch import AsyncElasticsearch  # 异步的 Elasticsearch 客户端

from app.entity.value_info import ValueInfo  # 取值实体：id、value（取值本身）、column_id（属于哪个字段）


class ColumnEsRepository:  # 定义"字段取值 ES 仓库"类
    _index_name = 'column_es_oy'  # index（ES 里的"索引"，相当于一张表）的名字，_oy 后缀用来和其他环境区分
    _index_mapping = {  # mapping（索引结构定义：规定有哪些字段、每个字段怎么存、怎么分词）
        'dynamic': False,  # 关掉动态映射：文档里出现没定义过的字段时，不允许自动加进索引
        "properties": {  # 下面是固定包含的字段
            "id":{'type':'keyword'},  # id 用 keyword（不分词，整串精确匹配）
            "value":{'type':'text',"analyzer": "ik_max_word","search_analyzer": "ik_max_word"},  # value 用 text 可分词，存和搜都用 ik_max_word（中文分词器，把句子切成尽量多的词）
            "column_id":{'type':'keyword'},  # column_id 也用 keyword，精确匹配
        }
    }
    def __init__(self, client:AsyncElasticsearch):  # 构造方法：传入 ES 客户端
        self.client = client  # 存下客户端，后面每个方法都用它和 ES 通信

    # 创建es索引
    async def createIndex(self):  # 创建索引（如果还不存在）
        if not await self.client.indices.exists(index= self._index_name):  # 先检查索引是否存在，不存在才创建（幂等：重复做结果一样，不会多出一份）
            await self.client.indices.create(  # 创建索引
                index = self._index_name,  # 索引名
                mappings= self._index_mapping  # 带上前面定义好的结构
            )

    async def insertIndex(self,values:list[ValueInfo],batch_size:int=20):  # 批量写入取值文档
        for i in range(0,len(values),batch_size):  # 每次跳 batch_size 步，把数据切成一批一批
            batch = values[i:i+batch_size]  # 取出当前这一批
            operations = []  # 准备一个空列表，装 bulk 批量操作要的内容
            for value in batch:  # 逐条处理这一批里的每个取值
                # 【注意】ES 批量操作要求文档 id 写在 index 里面（如 {"index":{...,"_id":...}}），这里 _id 写在了外面，很可能报格式错误
                operations.append({ "index" : { "_index" : self._index_name },"_id":value.id })  # 放一条"操作说明"：往哪个索引写、这条文档的 id
                # 添加文档数据
                operations.append(asdict(value))  # 紧接着放真正的文档内容（实体转成字典）
            await self.client.bulk(operations=operations)  # bulk（批量接口）：一次请求就把这一整批提交给 ES

    async def search(self,keyword:str,score_shreshold:float = 0.5,limit:int = 5):  # 按关键词搜取值
        # 【注意】参数名拼成了 score_shreshold（多了一个 h），正确拼写应为 threshold
        result = await self.client.search(  # 执行搜索
            index= self._index_name,  # 在哪个索引里搜
            query={  # 查询条件
                "match":{  # match：先分词再匹配（不是整串完全相等）
                    "value": keyword  # 拿关键字去匹配 value 字段
                }
            },
            size=limit,  # 最多返回几条
            min_score=score_shreshold,  # 相关度分数低于这个值的结果直接丢掉
        )
        print('es查询的数据为：',result)  # 打印 ES 的原始返回，方便调试排查
        # es 返回的固定数据结构，
        return [ValueInfo(**hit['_source']) for hit in result['hits']['hits']]  # 结果在 hits.hits 里，_source 是文档原文，逐个还原成 ValueInfo 列表
