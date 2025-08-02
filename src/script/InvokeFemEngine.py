import os
import time

import orjson
from tqdm import tqdm
from joblib import Parallel, delayed
from src.CheckTasks import init_tasks, check_task
from multiprocessing import Manager, Process, Lock, freeze_support, Pool

from src.common import script_generated_path
from src.common.enums import StatusEnum

tasks_json_path = os.path.join(script_generated_path,'tasks.json')
cases_json_path = os.path.join(script_generated_path,'cases.json')

cases = []
def worker(task_id,tasks):
    tasks[task_id]['status'] = 1

def invoke():
    # 将tasks设置为多进程共享变量，因为存在多进程更新任务状态的操作
    manager = Manager()
    # 无需设置为共享变量，不存在写操作，只需要读
    tasks = manager.list()
    # 检查任务集合json是否存在，以及更新cases、tasks用作临时信息集，便于记录状态和调用模型所需的相关信息
    if not os.path.exists(tasks_json_path):
        init_tasks(tasks_json_path,cases_json_path,tasks,cases,manager)
    else:
        with open(cases_json_path, 'rb') as f1, open(tasks_json_path, 'rb') as f2:
            cases[:] = orjson.loads(f1.read())
            raw_tasks = orjson.loads(f2.read())
            for t in tqdm(raw_tasks):
                tasks.append(manager.dict(t))

    pending_tasks = [task['task_id'] for task in tqdm(tasks,desc="正在筛选待执行任务") if task['status'] != 1]
    try:
        Parallel(n_jobs=os.cpu_count(), backend="loky")(
            delayed(worker)(task_id,tasks)
            for task_id in tqdm(pending_tasks, desc="Processing")
        )
    finally:
        serializable_tasks = [dict(t) for t in tqdm(tasks,desc='序列化任务表')]
        with open(tasks_json_path, 'wb') as f:
            f.write(orjson.dumps(serializable_tasks, option=orjson.OPT_INDENT_2))
    print("\nAll tasks done.")
    # with open(tasks_json_path, 'wb') as f:
    #     serializable_tasks = [dict(t) for t in tqdm(tasks,desc='序列化任务表')]
    #     f.write(orjson.dumps(serializable_tasks, option=orjson.OPT_INDENT_2))

if __name__ == '__main__':
    freeze_support()
    invoke()