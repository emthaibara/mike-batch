from joblib import Parallel, delayed

from src.aspect.start_simulation_aspect import load_and_persistence
from src.tools.tasks_tool import *

@load_and_persistence
def start_simulation(cases=None, pending_tasks=None):
    # 启动进程池,读取当前主机的cpu核心数量,根据核心数量确定进程池的最大并发进程量
    cpu_core_count = os.cpu_count()
    try:
        Parallel(n_jobs=cpu_core_count, backend="loky")(
            delayed(worker)(task_id,cases)
            for task_id in tqdm(pending_tasks, desc="发起水动力模型模拟任务")
        )
    except KeyboardInterrupt as e:
        print('\n意外退出，正在保存任务进度......')
        persistence()
        print('任务进度保存成功',end='False')
        print(e)
    finally:
        pass

def worker(task_id, cases):
    __rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # 更改状态为任务进行中⛔️
    __rd.hset(KEY, str(task_id), str(StatusEnum.in_process.value))

    # simulation
    work(cases[task_id])

    # 更改状态为已完成✅
    __rd.hset(KEY, str(task_id), str(StatusEnum.completed.value))

def work(case):
    case_path = case['path']
    q1 = case['q1']
    q2 = case['q2']
    q3 = case['q3']
    z0 = case['z0']
    duration = case['duration']

    pass

def work_test():

    case = {
        'path': './cases/case1.json',
        'q1': 2,
        'q2': 1,
        'q3': 1,
        'z0': 1,
        'duration': 1,
    }

if __name__ == '__main__':
    pass
    # r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # if os.path.exists(r'/Users/lemt/PycharmProjects/mike-batch/assets/generated/tasks.json'):
    #     os.remove(r'/Users/lemt/PycharmProjects/mike-batch/assets/generated/tasks.json')
    # if r.exists(KEY):
    #     r.delete(KEY)
    # start_simulation([],[])
