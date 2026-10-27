# ============================================================================
# 【文件说明】app/utils/loader_prompt_util.py —— 提示词模板读取工具
# 作用：按名字去项目根目录的 prompts/ 文件夹读 .prompt 文件，把文件里的文字原样返回。
# 谁用：app/agent/node/ 下的 column_call.py、metric_call.py、value_call.py、merge_retrieved.py，
#       它们调用 load_prompt_by_path('xxx') 拿提示词模板喂给大模型。
# ============================================================================
from pathlib import Path  # 导入 Path，用来拼文件路径


def load_prompt_by_path(fileName:str):  # 传入模板名（不带 .prompt 后缀），返回模板文字
    # 【作用】拼出 prompts/xxx.prompt 的绝对路径：parents[2] 从 utils 往上退两级到项目根目录
    path = Path(__file__).parents[2] / 'prompts' / f'{fileName}.prompt'  # f'...' 是字符串插值，把变量塞进路径
    return path.read_text(encoding='utf-8')  # 以 UTF-8 编码读整个文件并返回字符串（中文不会乱码）