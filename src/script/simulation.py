import math
import os
import shutil
import subprocess
import time
import picologging
from src.aspect import log_name
from src.common import simulation_path, mesh_path, dfsu_path, FemEngine_location
from src.enums import StatusEnum
from src.script import q1_key, q2_key, q3_key
from src.script.custom import gen_q1_q3_dfs0, gen_q2_dfs0, gen_m21fm
from src.tools import persistence, fill

__logger = picologging.getLogger(log_name)
pending_tasks = list()
cache_tasks = dict()
cases = dict()
def start_simulation():
    fill(cases, pending_tasks, cache_tasks)
    try:

        start_time = time.time()
        for task_id in pending_tasks:
            __work(task_id)
            __logger.info(f'🏳️‍🌈批量模拟已运行【{__get_elapsed_time_str(start_time)}】')

    except KeyboardInterrupt as e:
        __logger.info('⚠️意外退出，正在保存任务进度......')
        persistence(cache_tasks)
        __logger.info('任务进度保存成功')
        __logger.error(e)
    except subprocess.CalledProcessError as e:
        __logger.info('⚠️当前正在执行的任务异常，正在保存任务进度后退出......')
        persistence(cache_tasks)
        __logger.info('任务进度保存成功')
        __logger.error(e)
    finally:
        persistence(cache_tasks)

def __work(task_id):
    """ 任务状态修改=进行中 """
    cache_tasks[task_id] = StatusEnum.in_process
    __worker(task_id)
    """ 任务状态修改=已完成 """
    cache_tasks[task_id] = StatusEnum.completed
    """ 更新任务状态至tasks.json """
    persistence(cache_tasks)

def __worker(task_id):
    case = cases[task_id]
    """ 准备好必要的输入文件 """
    m21fm_path = __prepare_required_file(case)
    """ invoke FemEngine.exe 开始模拟（阻塞） """
    try:
        # 起始时间
        start_time = time.time()
        __logger.info(
            f'🚀该工况水动力模拟正在进行--->'
            f'编号ID：【{task_id}】,'
            f'描述信息：【{case['type']}】工况【z0={case['elevation']},q1={case[q1_key]},q2={case[q2_key]},q3={case[q3_key]},时长=[{case['duration']}h],步长={case['number_of_time_steps']}】,'
            f'路径：{case['path']}  '
            f'processing......')

        subprocess.run([FemEngine_location, m21fm_path, '/run'],
                       capture_output=False, text=True, check=True)
        elapsed_time = __get_elapsed_time_str(start_time)

        __logger.info(
            f'✅该工况水动力模拟已完成--->'
            f'编号ID:【{task_id}】,'
            f'描述信息:【{case['type']}】工况【z0={case['elevation']},q1={case[q1_key]},q2={case[q2_key]},q3={case[q3_key]},时长=[{case['duration']}h],步长={case['number_of_time_steps']}】,'
            f'路径:【{case['path']}】 '
            f'该工况模拟耗时:【{elapsed_time}】')

    except subprocess.CalledProcessError as e:
        cache_tasks[task_id] = StatusEnum.error
        __logger.error(f'⚠️模拟任务失败: {e}')
        raise e

def __prepare_required_file(case):
    """ 从case中获取信息：水位值（m21fm需要修改的高程值）、q1、q2、q3的目标流量、时间步长"""
    path = case['path']
    location = os.path.join(simulation_path, path)
    elevation = case['elevation']
    q1_flow_rate = case[q1_key]
    q2_flow_rate = case[q2_key]
    q3_flow_rate = case[q3_key]
    number_of_time_steps = case['number_of_time_steps']

    """ 定制化生成xxxx.dfs0,并写入对应目录 """
    gen_q1_q3_dfs0(number_of_time_steps, q1_flow_rate, 'Qlhk', location)
    gen_q2_dfs0(number_of_time_steps, q2_flow_rate, location)
    gen_q1_q3_dfs0(number_of_time_steps, q3_flow_rate, 'Qyg', location)

    """ 以母版定制化生成新m21fm配置文件,并写入对应目录：修改elevation、number_of_time_steps """
    m21fm_path = os.path.join(simulation_path, path, 'LHKHX.m21fm')
    gen_m21fm(elevation, number_of_time_steps, m21fm_path)

    """ 复制地形图 + 一维网格数据 """
    shutil.copy(str(dfsu_path), os.path.join(str(simulation_path), str(path), 'Manning.dfsu'))
    shutil.copy(str(mesh_path), os.path.join(str(simulation_path), str(path), 'LHKHX.mesh'))

    return m21fm_path

def __get_elapsed_time_str(start_time):
    # 结束时间
    end_time = time.time()
    # 耗时
    elapsed_time = end_time - start_time
    # 将总秒数转换为小时、分钟和秒
    hours = math.floor(elapsed_time / 3600)
    minutes = math.floor((elapsed_time % 3600) / 60)
    seconds = elapsed_time % 60
    # 将时间格式化为字符串
    return f"{int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒"