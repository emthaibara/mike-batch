# Introduce
本项目内容为实现批处理调用Mike提供的FemEngineHD.exe可执行文件进行水动力模型模拟

# Start
```shell
  uv venv
```
```shell
  uv sync
```
# 脚手架与核心库
mikeio + uv + multiprocessing + asyncio + orjson
# 脚本内容
1. case表生成
2. 层级目录生成（对应case表）
3. 检查 task表（第一次check则生成task表）,查看status(done,todo,inProgress)
4. 检查输入文件是否完整
5. 根据不同case设置输入文件
6. 批量调用FemEngineHD.exe
# 项目结构

# 性能优化

- 考虑到水动力模型模拟过程是一个计算密集型任务,单个case的运行时间较长,由于多进程比多线程更加适合计算密集型任务,本脚本采用多进程异步调用的方式尽可能充分利用多核CPU的优势加快整体的进度
- 多线程并发生成目录层级