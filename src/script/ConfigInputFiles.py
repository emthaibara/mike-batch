import os.path
import mikeio.dfsu
import numpy as np
import pandas as pd
from mikeio import Dfs0, ItemInfo, EUMType, EUMUnit
from src.common import assets_path

csv_path = os.path.join(assets_path,'test','Qout_LHK.csv')
dfs0_path = os.path.join(assets_path,'test','Qout_LHK_mikeio_write.dfs0')
def r_dfs0():
    dfs = Dfs0(dfs0_path)
    #读取所有数据并只保留整数
    data = dfs.read().to_dataframe().astype(int)
    #起始时间
    print('起始时间:',dfs.start_time)
    #时间间隔(整数输出)
    interval = dfs.to_dataframe().index[1] - dfs.to_dataframe().index[0]
    print('时间间隔:',int(interval.total_seconds()),'s')
    #每一行的值
    print('data:',data.values)
    # 列名
    print(dfs.items[0].name)
r_dfs0()

def w_dfs0(n : int,                     # 数据量（数据的行数）
           start_time : str,            # 起始时间
           time_step_seconds : int ,    # 时间间隔
           value : int or float,        # 因为不做变动,每一行的值都为value
           name : str,                  # 单位名称
           data_items_name : str,       # 数据项的列名称
           eum_type: EUMType,           # 数据类型
           eum_unit : EUMUnit,          # 对应的单位
           write_path : str,            # 写入位置,绝对路径
           ):
    # 时间序列,根据时间间隔和起始时间生成n个时间
    time_list = [pd.Timestamp(start_time) + pd.Timedelta(seconds=i * time_step_seconds) for i in range(n)]

    # 生成一维numpy数组 入参为 数据的结构（shape)与值(不做变动,为定值),只有一项数据的结构shape写法为（xx,）
    data = np.full((n,), value)

    # 将data包装为 DataFrame 用于后续的写入操作
    df = pd.DataFrame({data_items_name: data}, index=time_list)

    # 创建数据项,用于每一列的描述信息meta_data（单位名称,单位）
    meta_data = ItemInfo(name, eum_type, eum_unit)

    # 写入dfs0（即根据上述数据生成新的dfs0文件）,由于使用的mikeio版本为2.6.0与旧版的操作不一样,需要注意一下
    (mikeio
     .from_pandas(df, items=[meta_data])
     .to_dfs(write_path)
     )

def set_m21fm():

    pass
