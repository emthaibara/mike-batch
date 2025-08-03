import os
import platform
import orjson
from tqdm import tqdm
from joblib import Parallel, delayed
from src.Check import init_tasks
from multiprocessing import Manager,  freeze_support
from src.common import script_generated_path
from src.common.enums import StatusEnum
from src.Check import *

def invoke():
    # 将tasks设置为多进程共享变量,因为存在多进程更新任务状态的操作
    manager = Manager()
    tasks = manager.list() # TODO 还有待考量
    cases = []

    # 检查 cases.json, tasks.json 是否存在,检查顺序不可变动
    raw_cases = check_cases()
    raw_tasks = check_tasks()

    # TODO 任务状态的更新还有待考量,也行不需要tasks = manager.list(), 耗时太久了
    __load_data(raw_cases, raw_tasks, tasks, cases,manager)

    # 筛选未开始模拟的case
    pending_tasks = [task['task_id'] for task in tqdm(raw_tasks,desc="正在筛选待执行任务") if task['status'] != StatusEnum.COMPLETED.value]
    print('pending tasks:',len(pending_tasks))
    if len(pending_tasks) == 0:
        return

    # 启动进程池,读取当前主机的cpu核心数量,根据核心数量确定进程池的最大并发进程量
    cpu_core_count = os.cpu_count()
    print('current computer cpu_core_count:',cpu_core_count)
    try:
        Parallel(n_jobs=cpu_core_count, backend="loky")(
            delayed(__worker)(task_id,tasks,cases)
            for task_id in tqdm(pending_tasks, desc="发起水动力模型模拟任务")
        )
    finally:
        data = {'tasks':[]}
        for t in tqdm(tasks,desc='序列化tasks list'):
            data['tasks'].append(dict(t))
        with open(tasks_json_path, 'wb') as f:
            f.write(orjson.dumps(data))
    
    print("All tasks done | updated tasks.json")

# TODO 临时代码
def __load_data(raw_cases,raw_tasks,tasks,cases,manager):
    for t in tqdm(raw_tasks, desc='加载tasks list'):
        tasks.append(manager.dict(t))
    cases[:] = raw_cases[:]

#TODO: 调用水动力模型模拟引擎,并更新任务状态, 根据不同的任务设置不同的 dfs0 + m21fm   (具体修改哪些内容还不太明确)
def __worker(task_id,tasks,cases):
    tasks[task_id]['status'] = 1
    case = cases[task_id]['path']
    if not os.path.exists(os.path.join(script_generated_path,'simulation','all_case',case)):
        return

# test
if __name__ == '__main__':
    # mike模型模拟引擎 依赖windows 平台
    # TODO 后续启动脚本,入门位置先检查系统平台类型,非 windows 则抛异常
    p = platform.system()
    if p == 'Windows':
        freeze_support()
    print(f"当前系统为：{p}")
    invoke()