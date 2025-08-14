import math
import os
import shutil
import subprocess
import threading
import time
import picologging
from apscheduler.jobstores import redis
from colorama import Fore
from joblib import Parallel, delayed
from src.aspect import log_name, init_logging
from src.aspect.simulation_aspect import load_and_persistence
from src.common import simulation_path, rd_host, rd_port, mesh_path, dfsu_path, FemEngine_location
from src.enums import StatusEnum
from src.script import q1_key, q2_key, q3_key
from src.script.custom import gen_q1_q3_dfs0, gen_q2_dfs0, gen_m21fm
from src.tools import persistence, KEY, fresh_cash_tasks

__logger = picologging.getLogger(log_name)
@load_and_persistence
def start_simulation(cases=None, 
                     pending_tasks=None,
                     stop_event : threading.Event=None):
    """ 启动进程池,读取当前主机的cpu核心数量,根据核心数量确定进程池的最大并发进程量 """
    cpu_core_count = os.cpu_count()
    rd = redis.Redis(host=rd_host, port=rd_port, decode_responses=True)
    try:
        Parallel(n_jobs=cpu_core_count / 2, backend="loky")(
            delayed(worker)(task_id, cases, rd)
            for task_id in pending_tasks
        )
    except KeyboardInterrupt as e:
        stop_event.set()
        __logger.info('意外退出，正在保存任务进度......')
        fresh_cash_tasks()
        persistence()
        __logger.info('任务进度保存成功')
        __logger.error(e)
    finally:
        persistence()

def worker(task_id, cases, rd : redis.Redis):
    """ 更新状态为任务进行中⏳"""
    rd.hset(KEY, str(task_id), str(StatusEnum.in_process.value))
    """ simulation """
    work(cases[task_id])
    """ 更新状态为已完成✅ """
    rd.hset(KEY, str(task_id), str(StatusEnum.completed.value))
    rd.close()

def work(case):
    init_logging()
    logger = picologging.getLogger(log_name)
    """ 从case中获取信息：水位值（m21fm需要修改的高程值）、q1、q2、q3的目标流量、时间步长"""
    path = case['path']
    location = os.path.join(simulation_path, path)
    elevation = case['elevation']
    q1_flow_rate = case[q1_key]
    q2_flow_rate = case[q2_key]
    q3_flow_rate = case[q3_key]
    number_of_time_steps = case['number_of_time_steps']

    """ 定制化生成xxxx.dfs0,并写入对应目录 """
    gen_q1_q3_dfs0(number_of_time_steps,q1_flow_rate,'Qlhk',location)
    gen_q2_dfs0(number_of_time_steps, q2_flow_rate, location)
    gen_q1_q3_dfs0(number_of_time_steps, q3_flow_rate, 'Qyg', location)

    """ 以母版定制化生成新m21fm配置文件,并写入对应目录：修改elevation、number_of_time_steps """
    m21fm_path = os.path.join(simulation_path, path, 'LHKHX.m21fm')
    gen_m21fm(elevation, number_of_time_steps, m21fm_path)

    """ 复制地形图 + 一维网格数据 """
    shutil.copy(str(dfsu_path), os.path.join(str(simulation_path), str(path), 'Manning.dfsu'))
    shutil.copy(str(mesh_path), os.path.join(str(simulation_path), str(path), 'LHKHX.mesh'))

    """ invoke FemEngine.exe 开始模拟（阻塞） """
    # 起始时间
    start_time = time.time()
    logger.info(Fore.MAGENTA +f'⏳该工况水动力模拟正在进行--->【{case['type']}】工况【z0={elevation},q1={q1_flow_rate},q2={q2_flow_rate},q3={q3_flow_rate},步长={number_of_time_steps}】,path={path}  processing......')
    try:
        subprocess.run([FemEngine_location, m21fm_path, '/run'],
                       capture_output=False, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'⚠️模拟任务失败: {e}')
        raise e
    # 结束时间
    end_time = time.time()
    # 耗时
    elapsed_time = end_time - start_time
    # 将总秒数转换为小时、分钟和秒
    hours = math.floor(elapsed_time / 3600)
    minutes = math.floor((elapsed_time % 3600) / 60)
    seconds = elapsed_time % 60
    # 将时间格式化为字符串
    elapsed_time_str = f"{int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒"
    logger.info(Fore.MAGENTA  + f'✅该工况水动力模拟已完成--->【{case['type']}】工况【z0={elevation},q1={q1_flow_rate},q2={q2_flow_rate},q3={q3_flow_rate},步长={number_of_time_steps}】,path=【{path}】 该工况模拟耗时【{elapsed_time_str}】')


