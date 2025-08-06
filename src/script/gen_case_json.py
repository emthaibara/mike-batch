import itertools
import os
import orjson
from tqdm import tqdm
from src.common import script_generated_path
from src.tools import calculate_duration

def gen_cas_json(z0_cases_count,
                 q1_cases_count,
                 q2_cases_count,
                 q3_cases_count,
                 output_path=os.path.join(script_generated_path,'cases.json')):

    # 生成每个情况的所有可能值及其对应的数值
    q1_options = [(f"q1-{i + 1}", i + 1) for i in range(q1_cases_count)]
    q2_options = [(f"q2-{i + 1}", i + 1) for i in range(q2_cases_count)]
    q3_options = [(f"q3-{i + 1}", i + 1) for i in range(q3_cases_count)]
    z0_options = [(f"z0-{i + 1}", i + 1) for i in range(z0_cases_count)]

    # 所有组合，最后写入json文件
    all_combinations = {'cases': []}
    # 计数
    count = 0
    total = q1_cases_count * q2_cases_count * q3_cases_count * z0_cases_count
    # 使用 itertools.product 生成所有组合的笛卡尔积
    # combo 会是一个元组，例如 (('q1-1', 1), ('q2-1', 1), ('q3-1', 1), ('z0-1', 1))
    for combo_parts in tqdm(
        itertools.product(q1_options, q2_options, q3_options, z0_options),
        total=total,
        desc="生成case.json中",
    ):
        # 提取组合字符串部分和数值部分
        q1_str, q1_val = combo_parts[0]
        q2_str, q2_val = combo_parts[1]
        q3_str, q3_val = combo_parts[2]
        z0_str, z0_val = combo_parts[3]
        # 组合成完整的 case_id 字符串
        case_id_string = f"{z0_str}/{q1_str}/{q2_str}/{q3_str}"

        # 计算时长，如果时长为0跳过该case
        duration = calculate_duration(q1_str, q2_str, q3_str,z0_str)
        if duration <= 0:
            continue
        # 构建当前的组合对象
        current_case = {
            'case_id': count,
            'path':case_id_string,
            'z0': z0_str,
            'q1': q1_str,
            'q2': q2_str,
            'q3': q3_str,
            'duration': duration
        }
        count += 1
        all_combinations['cases'].append(current_case)

    # 将所有组合写入 JSON 文件
    try:
        with open(output_path, 'wb') as f:
            f.write(orjson.dumps(all_combinations,option=orjson.OPT_INDENT_2)) # 紧凑型
            tqdm.write(f"成功生成 {len(all_combinations['cases'])} 种组合，并保存到 '{output_path}' 文件")
    except IOError as e:
        print(f"写入文件时发生错误: {e}")


