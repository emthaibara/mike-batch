import os
import subprocess
import threading

from apscheduler.jobstores import redis
from joblib import Parallel, delayed
from tqdm import tqdm

from src.aspect.start_simulation_aspect import load_and_persistence
from src.common import simulation_path
from src.enums import StatusEnum
from src.script import q1_key, q2_key, q3_key
from src.script.custom import gen_m21fm,gen_dfs0
from src.tools import persistence, KEY


@load_and_persistence
def start_simulation(cases=None, pending_tasks=None,stop_event : threading.Event=None):
    # 启动进程池,读取当前主机的cpu核心数量,根据核心数量确定进程池的最大并发进程量
    cpu_core_count = os.cpu_count()
    try:
        Parallel(n_jobs=cpu_core_count, backend="loky")(
            delayed(worker)(task_id,cases)
            for task_id in tqdm(pending_tasks, desc="并发执行水动力模型模拟任务",position=0)
        )
    except KeyboardInterrupt as e:
        stop_event.set()
        tqdm.write('意外退出，正在保存任务进度......')
        persistence()
        tqdm.write('任务进度保存成功')
        print(e)
    finally:
        persistence()

def worker(task_id, cases):
    __rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
    # 更改状态为任务进行中⛔️
    __rd.hset(KEY, str(task_id), str(StatusEnum.in_process.value))
    # simulation
    work(cases[task_id])
    # 更改状态为已完成✅
    __rd.hset(KEY, str(task_id), str(StatusEnum.completed.value))

def work(case):
    path = case['path']
    location = os.path.join(simulation_path, path)
    elevation = case['elevation']
    q1_flow_rate = case[q1_key]
    q2_flow_rate = case[q2_key]
    q3_flow_rate = case[q3_key]
    number_of_time_steps = case['number_of_time_steps']
    # 定制 dfs0
    gen_dfs0(number_of_time_steps,q1_flow_rate,'Qlhk',location)
    gen_dfs0(number_of_time_steps, q2_flow_rate, 'Qcs', location)
    gen_dfs0(number_of_time_steps, q3_flow_rate, 'Qyg', location)
    # 定制 m21fm，修改elevation、number_of_time_steps
    gen_m21fm(elevation, number_of_time_steps, location)
    # TODO: invoke FemEngine.exe
    _FemEngine_location = r'C:\Program Files (x86)\DHI\2014\bin\x64\FemEngine.exe'
    command = f'{_FemEngine_location} run'
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e)