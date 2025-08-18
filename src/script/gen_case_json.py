import itertools
import os
import orjson
import pandas as pd
import picologging
from src.aspect import log_name
from src.common import required_path, q1_cases_file_name, q2_cases_file_name, q3_cases_file_name, do_nothing, \
    generate_electricity, pump, script_generated_path
from src.tools.calculate_tool import calculate_duration, get_z0_cases

__type = {
    generate_electricity : 'gen',
    pump : 'pump',
    do_nothing : 'do_nothing',
}
__logger = picologging.getLogger(log_name)
z0_key = f'elevation'
q1_key = f'q1-flow_rate'
q2_key = f'q2-flow_rate'
q3_key = f'q3-flow_rate'
# gen、pump、do_nothing
def __filter_case(case_type : str,
                  q2_offset,
                  count_offset):
    # 根据类型构建路径
    basic_location = os.path.join(required_path, __type[case_type])
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
    combinations = {f'{__type[case_type]}_cases':[]}
    count = 0
    for cases_id,combo in enumerate(itertools.product(z0_options, q1_options, q2_options, q3_options)):

        z0_value = z0_cases.loc[combo[0][0]].iloc[0]
        q1_value = q1_cases.loc[combo[1][0]].iloc[0]
        q2_value = q2_cases.loc[combo[2][0]].iloc[0]
        q3_value = q3_cases.loc[combo[3][0]].iloc[0]

        __logger.info("=======================================================================")
        __logger.info(f'{case_type}工况={combo[0][0]}/{combo[1][0]}/{combo[2][0]}/{combo[3][0]} 正在计算时长...')
        duration = calculate_duration(combo[0][0],q1_value,q2_value,q3_value)
        if duration <= 0:
            continue

        value = {
            'case_id' : count + count_offset,
            'path' : os.path.join(f'{combo[0][0]}-[{float(z0_value)}]',
                                  f'{combo[1][0]}-[{float(q1_value)}]',
                                  f'{combo[2][0]}-[{float(q2_value)}]',
                                  f'{combo[3][0]}-[{float(q3_value)}]'),
            z0_key : float(z0_value),
            q1_key : float(q1_value),
            q2_key : float(q2_value),
            q3_key : float(q3_value),
            'duration' : duration,
            'number_of_time_steps': int((duration * 3600) / 10),
            'type' : case_type,
        }
        count += 1
        combinations[f'{__type[case_type]}_cases'].append(value)
    try:
        write_path = os.path.join(script_generated_path, f'{__type[case_type]}_cases.json')
        with open(write_path, 'wb') as f:
            f.write(orjson.dumps(combinations, option=orjson.OPT_INDENT_2))
    except IOError as e:
        print(f"写入文件时发生错误: {e}")
    return combinations[f'{__type[case_type]}_cases']

def gen_cases_json():
    __cases = []

    __pump_cases = __filter_case(pump, 1, 0)
    __do_nothing_cases = __filter_case(do_nothing, 13, __pump_cases.__len__())
    __generate_electricity_cases = __filter_case(generate_electricity, 14, __do_nothing_cases.__len__() + __pump_cases.__len__())


    __logger.info(f"成功筛选有效[{f'{pump}_cases'}]工况共{__pump_cases.__len__()}种")
    __logger.info( f"成功筛选有效[{f'{do_nothing}_cases'}]工况共{__do_nothing_cases.__len__()}种")
    __logger.info(f"成功筛选有效[{f'{generate_electricity}_cases'}]工况共{__generate_electricity_cases.__len__()}种")

    __cases.extend(__pump_cases)
    __cases.extend(__do_nothing_cases)
    __cases.extend(__generate_electricity_cases)

    __logger.info(f"总的有效工况共{__cases.__len__()}种")
    __cases_json = {'cases' :  __cases}
    try:
        with open(os.path.join(script_generated_path, 'cases.json'), 'wb') as f:
            f.write(orjson.dumps(__cases_json, option=orjson.OPT_INDENT_2))
        __logger.info("=======================================================================")
    except IOError as e:
        __logger.error(f"写入文件时发生错误: {e}")
