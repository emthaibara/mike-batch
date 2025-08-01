# Introduce
本项目内容为实现批处理调用Mike提供的FemEngineHD.exe可执行文件进行水动力模型模拟
,本脚本依赖Mikeio库,需要windows7及其以上平台
# Start
```shell
  uv sync
```
# 脚手架与核心库
mikeio + uv + multiprocessing + asyncio + orjson
# 脚本内容
1. case表生成
2. 层级目录生成（对应case表）
3. 检查 task表（第一次check则生成task表）,查看status(done,todo,inProgress)
4. 检查输入文件集（dfs0、dfsu、mesh、m21fm）是否完整
5. 根据不同case设置输入文件（客制化写入新的dfs0以及m21fm描述文件）
6. 批量调用FemEngineHD.exe
# 项目结构

# 性能优化

- 多进程异步执行task
- 多线程并发生成目录层级
- 基于笛卡尔积快速生成所有cases