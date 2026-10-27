# 【文件作用】
# 这个文件是 PyCharm 新建项目时自动生成的模板（示例脚本），和 Text2SQL 主流程没有任何关系。
# 【注意】它现在只是测试 uuid5 的打印结果，基本可以直接删掉；真正跑主流程的入口在 app/agent/agent_graph.py。

# This is a sample Python script.
import uuid  # 导入标准库 uuid：用来生成唯一标识符（UUID，一长串几乎不会重复的字符）


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):  # 定义一个示例函数，接收一个名字
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # 上一行是 f-string（把变量直接塞进字符串）：打印 Hi, 名字；只是示例，主流程不会调用它


# Press the green button in the gutter to run the script.
if __name__ == '__main__':  # 只有"直接运行本文件"时才执行下面的代码；被别的文件 import 时不会执行
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "dim_region.region_id_0"))  # uuid5 = 按固定规则算 UUID：同一个字符串永远得到同一个 id（适合当向量库的记录 id）
    print(point_id)  # 打印算出来的 id
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "dim_region.region_id_1"))  # 换个名字再算一个（测试用）
    print(point_id)  # 打印第二个 id

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
