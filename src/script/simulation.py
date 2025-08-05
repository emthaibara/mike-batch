from joblib import Parallel, delayed

from src.aspect.start_simulation_aspect import load_and_persistence
from src.aspect.worker_aspect import update_task_status
from src.tools.tasks_tool import *

@load_and_persistence
def start_simulation(cases=None, pending_tasks=None):
    # 启动进程池,读取当前主机的cpu核心数量,根据核心数量确定进程池的最大并发进程量
    cpu_core_count = os.cpu_count()
    try:
        Parallel(n_jobs=cpu_core_count, backend="loky")(
            delayed(__worker)(task_id,cases)
            for task_id in tqdm(pending_tasks, desc="发起水动力模型模拟任务")
        )
    except BaseException as e:
        persistence()
        print(e)

# TODO: 调用水动力模型模拟引擎,并更新任务状态, 根据不同的任务设置不同的 dfs0 + m21fm   (具体修改哪些内容还不太明确)
@update_task_status
def __worker(task_id,cases):

    pass



if __name__ == '__main__':
    __worker(
        2131,
        {}
    )
