import math
import os.path
import subprocess
import threading
import time
from src.aspect import init_picologging, check
from src.common import cases_json_path, simulation_path, assets_path, generate_electricity, pump, do_nothing
from src.script import gen_cases_json, start_timing_job
from src.script.custom import gen_q1_q3_dfs0, gen_q2_dfs0, gen_m21fm
from src.script.gen_case_folder import gen_case_folder
from src.script.simulation import start_simulation
from src.script.statistics_cases import statistics_cases


# def _run_one_case_simulation():
#     """
#             {
#             "cases_id": 18234,
#             "path": "z0-13/q1-1/q2-1/q3-1",
#             "elevation": 2599,
#             "q1-flow_rate": 125,
#             "q2-flow_rate": -625,
#             "q3-flow_rate": 150,
#             "duration": 1.5,
#             "number_of_time_steps": 540,
#             "type": "pump"
#             },
#     """
#     location = os.path.join(assets_path,'test')
#     elevation = 2599
#     q1_flow_rate = 125
#     q2_flow_rate = -625
#     q3_flow_rate = 150
#     number_of_time_steps = 540
#     gen_q1_q3_dfs0(number_of_time_steps,
#                    q1_flow_rate,
#                    'Qlhk',
#                    location)
#     gen_q2_dfs0(number_of_time_steps,
#                 q2_flow_rate,
#                 location)
#     gen_q1_q3_dfs0(number_of_time_steps,
#                    q3_flow_rate,
#                    'Qyg',
#                    location)
#     gen_m21fm(elevation,
#               number_of_time_steps,
#               os.path.join(location,'LHKHX.m21fm'))
#     # 起始时间
#     start_time = time.time()
#     """ invoke FemEngine.exe 开始模拟 """
#     _FemEngine_location = r'C:\Program Files (x86)\DHI\2014\bin\x64\FemEngineHD.exe'
#     try:
#         subprocess.run([_FemEngine_location,os.path.join(assets_path,'test','LHKHX.m21fm'), '/run'],
#                        capture_output=True, text=True, check=True)
#         # 结束时间
#         end_time = time.time()
#         # 耗时
#         elapsed_time = end_time - start_time
#         # 将总秒数转换为小时、分钟和秒
#         hours = math.floor(elapsed_time / 3600)
#         minutes = math.floor((elapsed_time % 3600) / 60)
#         seconds = elapsed_time % 60
#         # 将时间格式化为字符串
#         elapsed_time_str = f"{int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒"
#         _type = {
#             generate_electricity: '发电',
#             pump: '抽水',
#             do_nothing: '不抽不发'
#         }
#         print(f'【抽水】工况【z0=2599,q1=125,q2=-625,q3=150】,水动力模拟已完成✅,该工况模拟耗时【{elapsed_time_str}】')
#     except subprocess.CalledProcessError as e:
#         print(e)

@init_picologging
@check
def main():
    """" 定时同步所有任务状态（每隔10s写入一次tasks.json） """
    stop_event = threading.Event()
    thread = threading.Thread(target=start_timing_job,args=(stop_event,))
    thread.start()
    """ 开始批量模拟（内容填充前置处理AOP独立出去了，这里传入空列表就行） """
    start_simulation([],[],stop_event=stop_event)

if __name__ == '__main__':
    main()