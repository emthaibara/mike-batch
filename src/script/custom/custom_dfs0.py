import os.path
import mikeio.dfsu
import numpy as np
import pandas as pd
from mikeio import Dfs0, ItemInfo, EUMType, EUMUnit
from src.common import assets_path

__start_time = '2023-01-01 08:00:00' #起始时间
__time_step_seconds = 10 # 秒
__preheat_time = 2160 # 0.6h x 3600s = 2160s
__number_of_preheat_steps = 216 # 2160 / 10 = 216
# TODO: 预热部份可能还需要修改
def gen_dfs0(number_of_time_steps : int,
             flow_rate: float,
             dfs0_type: str,     # 'Qlhk'---q1 'Qyg'----q3 'Qcs'----q2
             write_path) -> None:

    # 预热偏移量（流量匀速增长至flow_rate） 如果是Qcs偏移量设置为0
    offset = flow_rate / __number_of_preheat_steps if dfs0_type != 'Qcs' else 0
    # 时间序列
    time_list = [pd.Timestamp(__start_time) + pd.Timedelta(seconds=i * __time_step_seconds)
                 for i in range(__number_of_preheat_steps + number_of_time_steps)]
    # 准备数据
    # 预热部分
    part1 = np.full((__number_of_preheat_steps,),[i * offset for i in range(__number_of_preheat_steps)])
    part2 = np.full((number_of_time_steps,), flow_rate)
    data = np.concatenate([part1,part2])
    # 封装成mikeio需要的DataFrame
    df = pd.DataFrame({dfs0_type: data}, index=time_list)
    meta_data = ItemInfo(dfs0_type, EUMType.Discharge, EUMUnit.meter_pow_3_per_sec)
    # 写入dfs0（即根据上述数据生成新的dfs0文件）,由于使用的mikeio版本为2.6.0与旧版的操作不一样,需要注意一下
    (mikeio
     .from_pandas(df, items=[meta_data])
     .to_dfs(write_path)
     )

gen_dfs0(8,
         600,
         'Qlhk',
         r'C:\Users\Administrator\Desktop\mike-batch\assets\generated\q1-7-8h-accurate.dfs0')


csv_path = os.path.join(assets_path, 'test', 'Qout_LHK_mikeio_convert.csv')
def __dfs0_convert_to_csv():
    dsf0_path = os.path.join(assets_path, 'test', 'Qout_LHK.dfs0')
    data = Dfs0(dsf0_path).read()
    data.to_dataframe().to_csv(csv_path, index=True)
