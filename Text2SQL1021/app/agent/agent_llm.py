# 【文件作用】
# 这个文件只干一件事：按配置创建大模型客户端，并导出一个全局可用的 llm 对象。
# 节点（retrievalColumns / retrievalMetric / retrievalValue）都 import 这个 llm 去扩词和生成内容。
# ChatOpenAI（LangChain 里"按 OpenAI 接口规范聊天"的客户端类）。
# 因为 DeepSeek 提供了 OpenAI 兼容接口（地址、参数格式都一样），所以这里不用专门的 DeepSeek 类，直接用这个。
from langchain_openai import ChatOpenAI

# LLMConfig（大模型配置的类型：接口地址、密钥、模型名）；appConfig（读好的全局配置对象）
from app.conf.app_config import LLMConfig, appConfig


# 工厂函数（专门用来"造对象"的函数）：传入一份大模型配置，返回一个配好的 ChatOpenAI 客户端
# config: LLMConfig 是类型标注，只是提示调用方必须传这种配置，Python 运行时不会真的检查
def initLLM(config: LLMConfig):
    # 注意 return 后面有两个空格，属于原样保留的书写风格，不影响运行
    return  ChatOpenAI(
        base_url= config.base_url,  # 接口地址，例如 https://api.deepseek.com/v1（指向哪个服务）
        api_key= config.api_key,  # 调用凭证（密钥），从配置文件读取，不要写死在代码里
        model= config.model,  # 用哪个模型，例如 deepseek-chat
    )

# 模块导入时立刻执行一次：读出配置并创建好 llm，别处 import llm 拿到的就是这个现成对象。
# 【注意】因为是"导入时创建"，配置只读这一次；改了配置文件需要重启程序才会生效。
llm = initLLM(appConfig.llm)
