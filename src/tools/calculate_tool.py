import math
from functools import lru_cache
import pandas as pd
import picologging
from src.aspect import log_name, init_picologging
from src.common import z0_cases_path, v0_cases_path

__logger = picologging.getLogger(log_name)
# 为了代码的统一性，这里不对原先代码做变动，设置一个转换表 （z key <----> v的序号）
__key_to_num_dict = {f'z0-{i}': 16 - i for i in range(1, 16)}
__num_to_key_dict = {16 - i: f'z0-{i}' for i in range(1, 16)}
# TODO: 最短目标水位序号算式更新，并不加以时间限制输出图标验证规律
def __do_calculate(q1 : float,
                   q2 : float,
                   q3 : float,
                   z0_key : str) -> float:
    # 初始水位序号
    initial_water_level_num = __key_to_num_dict[z0_key] #15
    __logger.info(f'初始水位序号: {initial_water_level_num}')
    # 初始库容dq
    v0 = get_v0_cases().loc[z0_key].iloc[0] #4881
    __logger.info(f'初始库容dq: {v0}')
    # 净流量v0
    dq = q1 + q2 + q3 #-300
    __logger.info(f'净流量v0: {dq}')
    # 如果等于0，为了代码的统一性，我这里设置成无穷大，因为后面的算式他会做被除数
    if dq == 0:
        dq = float('inf')
    # 最大目标库容v1
    v1 = get_v0_cases().loc['z0-15' if dq < 0 else 'z0-1'].iloc[0]
    __logger.info(f'最大目标库容v1: {v1}')
    # 最长所需时间t1
    max_time_required_t1 = (v0 - v1) / (-dq) / 0.36
    __logger.info(f'最长所需时间T1: {max_time_required_t1}')
    # TODO: 限制后最短时间t1
    min_time_after_limit_t1 = min(max_time_required_t1, 10 if q2 < 0 else 7)
    __logger.info(f'限制后最短时间t1: {min_time_after_limit_t1}')
    # 最短目标水位序号
    if dq > 0:
        shortest_target_water_level_num = min(15,initial_water_level_num + 1)
    else:
        shortest_target_water_level_num = max(1,initial_water_level_num - 1)
    __logger.info(f'最短目标水位序号: {shortest_target_water_level_num}')
    # 最短目标水位序号对应的初始库容值
    shortest_target_water_level_key = __num_to_key_dict[shortest_target_water_level_num]
    # 最短目标库容v2
    v2 = get_v0_cases().loc[shortest_target_water_level_key].iloc[0]
    __logger.info(f'最短目标库容v2: {v2}')
    # 最短所需时间t2
    min_time_required_t2 = (v0 - v2) / (-dq) / 0.36
    __logger.info(f'最短所需时间T2: {min_time_required_t2}')
    # TODO: 限制后最短时间t2
    min_time_after_limit_t2 = min(min_time_required_t2,5)
    __logger.info(f'限制后最短时间T2: {min_time_after_limit_t2}')
    # 计算时长 = 插值系数 * 计算时常
    #获取插值系数
    interpolation_factor = __get_interpolation_factor(q1 ,q2 ,q3)
    __logger.info(f'最终插值系数: {interpolation_factor}')
    # 开始计算
    time = min_time_after_limit_t2 + (min_time_after_limit_t1 - min_time_after_limit_t2) * interpolation_factor
    # 四舍五入保留小数点后两位
    # 向上取，例如：6.19，6.05，6.22 ----> 6.5h
    result = roundup_excel(time / 0.5, 0) * 0.5
    __logger.info(f'最终计算时长为: {result}')
    return result

def roundup_excel(number, decimal_places):
    """模拟 Excel ROUNDUP 的行为，总是远离零点取整。"""
    multiplier = 10**decimal_places
    if number >= 0:
        return math.ceil(number * multiplier) / multiplier
    else:
        return math.floor(number * multiplier) / multiplier

# 计算插值系数
def __get_interpolation_factor(q1 : float ,q2 : float ,q3 : float)->float:
    interpolation_factor = 0
    if q2 <= -500:
        interpolation_factor = 0.85 # 抽水最严重
    elif -500 < q2 <= -400:
        interpolation_factor = 0.7 # 抽水很严重
    elif -400 < q2 <= -200:
        interpolation_factor = 0.45 # 抽水较严重
    elif -200 < q2 < 0:
        interpolation_factor = 0.3 # 抽水一般
    elif 0 <= q2 < 200:
        interpolation_factor = 0.15 # 不用抽水
    elif q2 >= 200:
        interpolation_factor = 0.05 # 发电较多
    # 发电或不抽不发直接返回插值系数不需要修正
    if q2 >= 0:
        return interpolation_factor
    else:
        # 修正
        diff = q1 - q3
        if diff <= -600:
            interpolation_factor += 0.15 # 水减很加剧
        elif -600 < diff <= -00:
            interpolation_factor += 0.1 # 水减很加剧
        elif -300 < diff < 0:
            interpolation_factor += 0.1 # 水减加剧
        elif 0 <= diff < -300:
            interpolation_factor -= 0.15 # 水增减缓
        elif diff >= 300:
            interpolation_factor -= 0.25 # 水增很减缓
        return interpolation_factor

#  不缓存的话8万个case会奇慢无比
@lru_cache(maxsize=2)
def __load_cases(cases_path : str) -> pd.DataFrame:
    return pd.read_csv(cases_path,index_col=0,header=None)

# 对外暴露的获取xxx_cases.csv的操作函数
def get_v0_cases():
    return __load_cases(v0_cases_path)
def get_z0_cases():
    return __load_cases(z0_cases_path)

# 计算时长入口
def calculate_duration(z0_key : str,
                       q1_value : float,
                       q2_value : float,
                       q3_value : float) -> float:
    return __do_calculate(q1_value, q2_value, q3_value, z0_key)

# print(calculate_duration('z0-5',280,125,230))