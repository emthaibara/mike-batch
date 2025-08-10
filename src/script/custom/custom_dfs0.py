import os.path
import mikeio.dfsu
import numpy as np
import pandas as pd
from mikeio import ItemInfo, EUMType, EUMUnit, Dfs0
from src.common import assets_path
from tools.permissions_tool import set_file_only_read

__start_time = '2023-01-01 08:00:00' #起始时间
__time_step_seconds = 10 # 秒

"""
q1,q3预热阶段分为4个
1）小流量启动0-10min，从0到100
2）稳定流量10-20min，固定100
3）小流量过渡到目标流量20-30或45min，从100到Q1（按速率控制时间，Q1小，就是20-30min，Q1大就是20-45min）
4）目标流量稳定30或45min-60min，固定Q1
"""
__dividing = 360.0
def gen_q1_q3_dfs0(number_of_time_steps : int,
             flow_rate: float,
             dfs0_type: str,     # 'Qlhk'---q1 'Qyg'----q3
             write_path) -> None:
    """ 预热阶段一 10min 偏移量固定=100/60=1.68 """
    number_of_stage_one_preheat_time_steps = 60
    stage_one_offest = round(100 / number_of_stage_one_preheat_time_steps,2)
    stage_one_data = np.full((number_of_stage_one_preheat_time_steps,),
                             [ stage_one_offest * i for i in range(number_of_stage_one_preheat_time_steps) ])
    # print('预热阶段一:',stage_one_data,'0-10min步长为：',stage_one_data.__len__())

    """ 预热阶段二 10min """
    number_of_stage_two_preheat_time_steps = 60
    stage_two_data = np.full((number_of_stage_two_preheat_time_steps,),100)
    # print('预热阶段二 :',stage_two_data,'10min-20min步长为：',stage_two_data.__len__())

    """ 预热阶段三 q1小流量=10min  q1大流量=15min """
    number_of_stage_three_preheat_time_steps = int(((10 if flow_rate < __dividing else 25) * 60) / __time_step_seconds)
    stage_three_offest = round((flow_rate - 100) / number_of_stage_three_preheat_time_steps,2)
    stage_three_data = np.full((number_of_stage_three_preheat_time_steps,),
                               [ 100 + stage_three_offest * (i+1) for i in range(number_of_stage_three_preheat_time_steps) ])
    # print('预热阶段三:',stage_three_data,'20min-30min步长为：',stage_three_data.__len__())

    """ 预热阶段四  q1小流量=15min  q2大流量=20分钟"""
    number_of_stage_four_preheat_time_steps = int(((30 if flow_rate < __dividing else 15) * 60) / __time_step_seconds)
    stage_four_data = np.full((number_of_stage_four_preheat_time_steps + 1,),flow_rate)
    # print('预热阶段四:',stage_four_data,'30min-60min步长为：',stage_four_data.__len__())

    """ 目标流量 """
    stage_five_data = np.full((number_of_time_steps,),flow_rate)

    """ 合并 """
    data = np.concatenate([stage_one_data,
                           stage_two_data,
                           stage_three_data,
                           stage_four_data,
                           stage_five_data])

    # 时间序列
    time_list = [pd.Timestamp(__start_time) + pd.Timedelta(seconds=i * __time_step_seconds)
                 for i in range(data.__len__())]
    # 封装成mikeio需要的DataFrame
    df = pd.DataFrame({dfs0_type: data}, index=time_list)
    meta_data = ItemInfo(dfs0_type, EUMType.Discharge, EUMUnit.meter_pow_3_per_sec)

    # 写入dfs0（即根据上述数据生成新的dfs0文件）,由于使用的mikeio版本为2.6.0与旧版的操作不一样,需要注意一下
    path = os.path.join(write_path,f'{'Qout_LHK' if dfs0_type == 'Qlhk' else 'Qout_YGYJ'}.dfs0')
    (mikeio
     .from_pandas(df, items=[meta_data])
     .to_dfs(path)
     )

def gen_q2_dfs0(number_of_time_steps : int,
             flow_rate: float,
             write_path):
    data = np.concatenate([np.full((361,),0), np.full((number_of_time_steps,),flow_rate)])
    time_list = [pd.Timestamp(__start_time) + pd.Timedelta(seconds=i * __time_step_seconds)
                 for i in range(data.__len__())]
    # 封装成mikeio需要的DataFrame
    df = pd.DataFrame({'Qcs': data}, index=time_list)
    meta_data = ItemInfo('Qcs', EUMType.Discharge, EUMUnit.meter_pow_3_per_sec)
    path  = os.path.join(write_path,'Qcs_LHKHX.dfs0')
    (mikeio
     .from_pandas(df, items=[meta_data])
     .to_dfs(path)
     )

def __dfs0_convert_to_csv():
    dsf0_path = os.path.join(assets_path, 'test', 'Qout_LHK.dfs0')
    data = Dfs0(dsf0_path).read()
    data.to_dataframe().to_csv(os.path.join(assets_path, 'test', 'Qout_LHK_mikeio_convert.csv'), index=True)
