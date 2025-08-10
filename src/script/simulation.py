import os
import subprocess
import threading

import picologging
from apscheduler.jobstores import redis
from joblib import Parallel, delayed
from tqdm import tqdm

from src.aspect import log_name
from src.aspect.simulation_aspect import load_and_persistence
from src.common import simulation_path
from src.enums import StatusEnum
from src.script import q1_key, q2_key, q3_key
from src.script.custom import gen_q1_q3_dfs0, gen_q2_dfs0, gen_m21fm
from src.tools import persistence, KEY

__logger = picologging.getLogger(log_name)
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
        __logger.info('意外退出，正在保存任务进度......')
        persistence()
        __logger.info('任务进度保存成功')
        __logger.error(e)
    finally:
        persistence()

def worker(task_id, cases):
    # __rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rd = redis.Redis(host='192.168.31.253', port=6379, decode_responses=True)
    # 更新状态为任务进行中⛔️
    rd.hset(KEY, str(task_id), str(StatusEnum.in_process.value))
    # simulation
    work(cases[task_id])
    # 更新状态为已完成✅
    rd.hset(KEY, str(task_id), str(StatusEnum.completed.value))

def work(case):
    """ 从case中获取信息：水位值（m21fm需要修改的高程值）、q1、q2、q3的目标流量、时间步长"""
    path = case['path']
    location = os.path.join(simulation_path, path)
    elevation = case['elevation']
    q1_flow_rate = case[q1_key]
    q2_flow_rate = case[q2_key]
    q3_flow_rate = case[q3_key]
    number_of_time_steps = case['number_of_time_steps']
    """ 定制化生成xxxx.dfs0，并写入对应目录 """
    gen_q1_q3_dfs0(number_of_time_steps,q1_flow_rate,'Qlhk',location)
    gen_q2_dfs0(number_of_time_steps, q2_flow_rate, location)
    gen_q1_q3_dfs0(number_of_time_steps, q3_flow_rate, 'Qyg', location)
    """ 以母版定制化生成新m21fm配置文件，并写入对应目录：修改elevation、number_of_time_steps """
    m21fm_path = os.path.join(simulation_path, 'LHKHX.m21fm')
    gen_m21fm(elevation, number_of_time_steps, m21fm_path)

    """ invoke FemEngine.exe 开始模拟（阻塞） """
    _FemEngine_location = r'C:\Program Files (x86)\DHI\2014\bin\x64\FemEngineHD.exe'
    try:
        subprocess.run([_FemEngine_location, m21fm_path, '/run'],
                       capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        __logger.error(e)
