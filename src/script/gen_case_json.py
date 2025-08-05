import itertools
import logging
import os

import orjson
from tqdm import tqdm

from src.common import script_generated_path


def gen_cas_json(q1_count, q2_count, q3_count, z0_count, output_filename=os.path.join(script_generated_path,'cases.json')):
    """
    生成 q1, q2, q3, z0 的所有组合，并将其保存为 JSON 文件。
    每个组合除了包含完整的 case_id 字符串，还会包含 q1, q2, q3, z0 的单独数值。

    Args:
        q1_count (int): q1 的情况数量。
        q2_count (int): q2 的情况数量。
        q3_count (int): q3 的情况数量。
        z0_count (int): z0 的情况数量。
        output_filename (str): 输出 JSON 文件的名称。
    """

    # 生成每个情况的所有可能值及其对应的数值
    q1_options = [(f"q1-{i + 1}", i + 1) for i in range(q1_count)]
    q2_options = [(f"q2-{i + 1}", i + 1) for i in range(q2_count)]
    q3_options = [(f"q3-{i + 1}", i + 1) for i in range(q3_count)]
    z0_options = [(f"z0-{i + 1}", i + 1) for i in range(z0_count)]

    all_combinations = {'cases': []}
    count = 0
    total = q1_count * q2_count * q3_count * z0_count
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

        # 构建当前的组合对象
        current_case = {
            'case_id': count,
            'path':case_id_string,
            'z0': z0_val,
            'q1': q1_val,
            'q2': q2_val,
            'q3': q3_val,
            'duration': 28800  # TODO： 8h = 8x 3600 = 28800s  后续要根据实际case生成
        }
        count += 1
        all_combinations['cases'].append(current_case)

    # 将所有组合写入 JSON 文件
    try:
        with open(output_filename, 'wb') as f:
            f.write(orjson.dumps(all_combinations)) # 紧凑型
            # f.write(orjson.dumps(all_combinations,option=orjson.OPT_INDENT_2)) 格式化输出 ：）
            print(f"成功生成 {len(all_combinations)} 种组合，并保存到 '{output_filename}' 文件。")
    except IOError as e:
        print(f"写入文件时发生错误: {e}")

# 定义每种情况的数量  25x15x15x15 = 84374
q1_cases = 25
q2_cases = 15
q3_cases = 15
z0_cases = 15

# 执行函数
gen_cas_json(
    q1_cases,
    q2_cases,
    q3_cases,
    z0_cases,)