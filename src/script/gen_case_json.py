import itertools
import os

import orjson
import pandas as pd
from colorama import Fore
from tqdm import tqdm

from src.common import required_path, q1_cases_file_name, q2_cases_file_name, q3_cases_file_name, do_nothing, \
    generate_electricity, pump, script_generated_path
from src.tools import get_z0_cases, KEY
from src.tools.calculate_tool import calculate_duration

__type = {
    generate_electricity : '发电',
    pump : '抽水',
    do_nothing : '不抽不发'
}

z0_key = f'elevation'
q1_key = f'q1-flow_rate'
q2_key = f'q2-flow_rate'
q3_key = f'q3-flow_rate'
# gen、pump、do_nothing
def __filter_case(case_type : str,q2_offset,count_offset):
    # 根据类型构建路径
    basic_location = os.path.join(required_path, case_type)
    q1_cases_path = os.path.join(basic_location, q1_cases_file_name)
    q2_cases_path = os.path.join(basic_location, q2_cases_file_name)
    q3_cases_path = os.path.join(basic_location, q3_cases_file_name)
    # 读取数据
    q1_cases = pd.read_csv(q1_cases_path,index_col=0,header=None)
    q2_cases = pd.read_csv(q2_cases_path,index_col=0,header=None)
    q3_cases = pd.read_csv(q3_cases_path,index_col=0,header=None)
    z0_cases = get_z0_cases()

    q1_total = q1_cases.__len__()
    q2_total = q2_cases.__len__()
    q3_total = q3_cases.__len__()
    z0_total = z0_cases.__len__()

    # 构建序列
    q1_options = [(f"q1-{i + 1}", i + 1) for i in range(q1_total)]
    q2_options = [(f"q2-{q2_offset + i}", i + 1) for i in range(q2_total)]
    q3_options = [(f"q3-{i + 1}", i + 1) for i in range(q3_total)]
    z0_options = [(f"z0-{i + 1}", i + 1) for i in range(z0_total)]
    # json
    combinations = {f'{case_type}_cases':[]}
    # 总计
    total = q1_total * q2_total * q3_total * z0_total
    count = 0
    for cases_id,combo in tqdm(
        enumerate(itertools.product(q1_options, q2_options, q3_options, z0_options)),
        total=total,
        desc=f"正在筛选所有[{__type[case_type]}]工况中",
    ):
        z0_value = z0_cases.loc[combo[3][0]].iloc[0]
        q1_value = q1_cases.loc[combo[0][0]].iloc[0]
        q2_value = q2_cases.loc[combo[1][0]].iloc[0]
        q3_value = q3_cases.loc[combo[2][0]].iloc[0]

        duration = calculate_duration(combo[3][0],q1_value,q2_value,q3_value)
        if duration <= 0:
            continue

        value = {
            'cases_id' : count + count_offset,
            'path' : f'{combo[3][0]}/{combo[0][0]}/{combo[1][0]}/{combo[2][0]}',
            z0_key : int(z0_value),
            q1_key : int(q1_value),
            q2_key : int(q2_value),
            q3_key : int(q3_value),
            'duration' : duration,
            'number_of_time_steps': int((duration * 3600) / 10),
            'type' : case_type,
        }
        count += 1
        combinations[f'{case_type}_cases'].append(value)
    try:
        write_path = os.path.join(script_generated_path, f'{case_type}_cases.json')
        with open(write_path, 'wb') as f:
            f.write(orjson.dumps(combinations, option=orjson.OPT_INDENT_2))
    except IOError as e:
        print(f"写入文件时发生错误: {e}")
    return combinations[f'{case_type}_cases']

def gen_cases_json():
    __cases = []
    __do_nothing_cases = __filter_case(do_nothing, 13, 0)
    __generate_electricity_cases = __filter_case(generate_electricity, 14, __do_nothing_cases.__len__())
    __pump_cases = __filter_case(pump, 1, __do_nothing_cases.__len__()+__generate_electricity_cases.__len__())

    print( f"{Fore.GREEN}成功筛选有效[{f'{do_nothing}_cases'}]工况共{__do_nothing_cases.__len__()}种")
    print(f"{Fore.GREEN}成功筛选有效[{f'{generate_electricity}_cases'}]工况共{__generate_electricity_cases.__len__()}种")
    print(f"{Fore.GREEN}成功筛选有效[{f'{pump}_cases'}]工况共{__pump_cases.__len__()}种")

    __cases.extend(__do_nothing_cases)
    __cases.extend(__generate_electricity_cases)
    __cases.extend(__pump_cases)
    print(f"{Fore.GREEN}总的有效工况共{__cases.__len__()}种")
    __cases_json = [KEY, __cases]
    try:
        with open(os.path.join(script_generated_path, 'cases.json'), 'wb') as f:
            f.write(orjson.dumps(__cases_json, option=orjson.OPT_INDENT_2))
    except IOError as e:
        print(f"写入文件时发生错误: {e}")
