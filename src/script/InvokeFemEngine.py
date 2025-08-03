import os
import platform
import orjson
from tqdm import tqdm
from joblib import Parallel, delayed
from src.CheckTasks import init_tasks
from multiprocessing import Manager,  freeze_support
from src.common import script_generated_path
from src.common.enums import StatusEnum

tasks_json_path = os.path.join(script_generated_path,'tasks.json')
cases_json_path = os.path.join(script_generated_path,'cases.json')
def invoke():
    # 将tasks设置为多进程共享变量，因为存在多进程更新任务状态的操作
    manager = Manager()
    tasks = manager.list()
    cases = []
    # 检查任务集合json是否存在，以及更新cases、tasks用作临时信息集，便于记录状态和调用模型所需的相关信息
    if not os.path.exists(tasks_json_path):
        init_tasks(tasks_json_path,cases_json_path,tasks,cases,manager)
    else:
        with open(cases_json_path, 'rb') as f1, open(tasks_json_path, 'rb') as f2:
            cases[:] = orjson.loads(f1.read())['cases']
            raw_tasks = orjson.loads(f2.read())['tasks']
            for t in tqdm(raw_tasks,desc='初始化任务列表中：'):
                tasks.append(manager.dict(t))
    
    pending_tasks = [task['task_id'] for task in tqdm(tasks,desc="正在筛选待执行任务") if task['status'] != StatusEnum.COMPLETED.value]
    print('pending tasks:',len(pending_tasks))
    if len(pending_tasks) == 0:
        return

    cpu_core_count = os.cpu_count()
    print('current computer cpu_core_count:',cpu_core_count)
    try:
        Parallel(n_jobs=cpu_core_count, backend="loky")(
            delayed(worker)(task_id,tasks,cases)
            for task_id in tqdm(pending_tasks, desc="发起水动力模型模拟任务")
        )
    finally:
        data = {'tasks':[]}
        for t in tqdm(tasks,desc='序列化任务表'):
            data['tasks'].append(dict(t))
        with open(tasks_json_path, 'wb') as f:
            f.write(orjson.dumps(data))
    
    print("All tasks done | updated tasks.json")

def worker(task_id,tasks,cases):
    tasks[task_id]['status'] = 1
    case = cases[task_id]['path']
    if not os.path.exists(os.path.join(script_generated_path,'simulation','all_case',case)):
        return

if __name__ == '__main__':
    match platform.system():
        case 'Windows':
            freeze_support()
        case _ as p:
            print(f"当前系统平台为：{p}")
    invoke()