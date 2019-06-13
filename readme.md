# MAA for E-VRPTW
一个多主体算法，适用于 E-VRPTW(Electric Vehicle Routing Problem with Time Windows)。
## Usage
在根目录下执行 `python main.py` 命令执行。

可能用到的常量有：
-  迭代次数 (在 `main.py` 开头)
	- 尝试优化整体路径的次数，耗时(时钟周期)约为节点数平方$ \times 300$。
- 输入文件 (在 `main.py` 开头)
	- edgeFile, nodeFile, initFile, outputFile 分别表示边集文件，配送中心/顾客需求/充电站文件，充电站选择文件，**输出解答文件**。
	- 充电站选择文件的使用请参照 `main.py` 最后注释处。
	- 注意配送中心的编号应为0。
	- 如更换读入方法请修改 `\agent` 中的读入文件。
- 全局变量(在 `agent\constants.py`)
	- 包括路径花费，车辆信息等，与单个结点无关的变量。

## Environment and dependent
Windows 10 (x86_64)

Python veresion = 3.5.2

仅依赖于 Python 标准库

