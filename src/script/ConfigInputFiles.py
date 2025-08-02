import os.path

import mikeio.dfsu
import numpy as np
import pandas as pd
from mikeio import Dfs0, ItemInfo, EUMType, EUMUnit
from src.common import assets_path

csv_path = os.path.join(assets_path, 'test', 'Qout_LHK.csv')
dfs0_path = os.path.join(assets_path, 'test', 'Qout_LHK_mikeio_write.dfs0')


def r_dfs0():
    dfs = Dfs0(dfs0_path)
    # 读取所有数据并只保留整数
    data = dfs.read().to_dataframe().astype(int)
    # 起始时间
    print('起始时间:', dfs.start_time)
    # 时间间隔(整数输出)
    interval = dfs.to_dataframe().index[1] - dfs.to_dataframe().index[0]
    print('时间间隔:', int(interval.total_seconds()), 's')
    # 每一行的值
    print('data:', data.values)
    # 列名
    print(dfs.items[0].name)


def w_dfs0(n: int,  # 数据量（数据的行数）
           start_time: str,  # 起始时间
           time_step_seconds: int,  # 时间间隔
           value: int or float,  # 因为不做变动,每一行的值都为value
           preheat_value: int,  # 预热值
           preheat_time: int,  # 预热时间,单位秒
           unit_nickname: str,  # 单位名称
           data_items_name: str,  # 数据项的列名称
           write_path: str,  # 写入位置,绝对路径
           ):
    # 时间序列,根据时间间隔和起始时间生成n个时间
    time_list = [pd.Timestamp(start_time) + pd.Timedelta(seconds=i * time_step_seconds) for i in range(n)]

    # 生成一维numpy数组 入参为 数据的结构（shape)与值(不做变动,为定值),只有一项数据的结构shape写法为（xx,）
    #  mikeio文档描述传入数据要求：  fill_value 为固定值或数组
    # 准备values,前1h为预热数据,10s时间间隔,前3600/10=360行为预热数据,360-n行为固定值values
    preheat_row = int(preheat_time / time_step_seconds)
    values = np.concatenate((np.full((preheat_row,), preheat_value), np.full((n - preheat_row,), value)))

    # 将data包装为 DataFrame 用于后续的写入操作
    df = pd.DataFrame({data_items_name: values}, index=time_list)

    # 创建数据项,用于每一列的描述信息meta_data（单位名称,单位）
    meta_data = ItemInfo(unit_nickname, EUMType.Discharge, EUMUnit.meter_pow_3_per_sec)

    # 写入dfs0（即根据上述数据生成新的dfs0文件）,由于使用的mikeio版本为2.6.0与旧版的操作不一样,需要注意一下
    (mikeio
     .from_pandas(df, items=[meta_data])
     .to_dfs(write_path)
     )

# 调用示例
# w_dfs0(
#     3001,
#     start_time='2022-01-01 08:40:00',
#     time_step_seconds=10,
#     value=600,
#     preheat_value=600,
#     preheat_time=3600,
#     unit_nickname='Qlhk',
#     data_items_name='Qlhk',
#     write_path=os.path.join(assets_path, 'test', 'Qout_LHK_mikeio_write.dfs0')
# )

m21fm_path = os.path.join(assets_path, 'test', 'LHKHX.m21fm')
format_m21fm_path = os.path.join(assets_path, 'test', 'Script-gen-LHKHX.m21fm')
def format_m21fm():
    with open(m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(format_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)

# format_m21fm()

Scripts_set_m21fm_path = os.path.join(assets_path, 'test', 'Script-set-gen-LHKHX.m21fm')
# 逐行读取并原地修改再写入新文件
def config_m21fm(surface_elevation_constant: float):
    with open(format_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    target = 'surface_elevation_constant'
    first_appear_target_row = -1
    old_target_row = ''
    # 需要修改的目标属性位于首次出现的位置,记录第一次出现位置就行
    for i, line in enumerate(lines):
        if target in line:
            old_target_row = line
            first_appear_target_row = i
            break

    parts = old_target_row.split('= ')
    new_target_row = f'{parts[0]}= {str(surface_elevation_constant)}\n'

    # 拼接成新的m21fm context
    l1 = lines[:first_appear_target_row]
    l1.append(new_target_row)
    l2 = lines[first_appear_target_row+1:]
    new_m21fm_context = l1 + l2

    # 写入新文件
    with open(Scripts_set_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_m21fm_context)

# config_m21fm(2599.5)


