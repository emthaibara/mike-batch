import os.path
import threading
import time

import picologging

from src.aspect import init_picologging, log_name
from src.common import cases_json_path, simulation_path, assets_path
from src.script import gen_cases_json, start_timing_job
from src.script.custom import gen_q1_q3_dfs0, gen_q2_dfs0, gen_m21fm
from src.script.gen_case_folder import gen_case_folder
# from src.script.simulation import start_simulation
from src.script.statistics_cases import statistics_cases

@init_picologging
def main():
    """ 生成工况组合并根据计算时常筛选出有效工况 """
    gen_cases_json()
    statistics_cases()
    # """" 根据工况表批量生成工况目录 """
    # gen_case_folder(cases_json_path,simulation_path,max_workers=12)
    # """" 定时同步所有任务状态（每隔10s写入一次tasks.json） """
    # time.sleep(5)
    # stop_event = threading.Event()
    # thread = threading.Thread(target=start_timing_job,args=(stop_event,))
    # thread.start()
    # """ 开始批量模拟（内容填充前置处理AOP独立出去了，这里传入空列表就行） """
    # start_simulation([],[],stop_event=stop_event)

@init_picologging
def log_test():
    logger = picologging.getLogger(log_name)
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

# @init_picologging
# def _test():
#     """ 生成工况组合并根据计算时常筛选出有效工况 """
#     gen_cases_json()
#     time.sleep(0.5)
#     statistics_cases()
#     """" 根据工况表批量生成工况目录 """
#     gen_case_folder(cases_json_path, simulation_path, max_workers=12)

""" 
    {
      "cases_id": 18234,
      "path": "z0-13/q1-1/q2-1/q3-1",
      "elevation": 2599,
      "q1-flow_rate": 125,
      "q2-flow_rate": -625,
      "q3-flow_rate": 150,
      "duration": 1.5,
      "number_of_time_steps": 540,
      "type": "pump"
    }, 
"""
def _run_one_case_simulation():
    location = os.path.join(assets_path,'test')
    elevation = 2599
    q1_flow_rate = 125
    q2_flow_rate = -625
    q3_flow_rate = 150
    number_of_time_steps = 540
    gen_q1_q3_dfs0(number_of_time_steps,q1_flow_rate,'Qlhk',location)
    gen_q2_dfs0(number_of_time_steps,q2_flow_rate,location)
    gen_q1_q3_dfs0(number_of_time_steps,q3_flow_rate,'Qyg',location)
    gen_m21fm(elevation,number_of_time_steps,location)

if __name__ == '__main__':
    main()
    # main()