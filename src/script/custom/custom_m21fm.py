import os.path
from src.common import assets_path, origin_m21fm_path
from tools.permissions_tool import set_file_only_read


# 格式化m21fm：去掉所有空行，紧凑布局
def __format_m21fm():
    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(origin_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)
__format_m21fm()

# 逐行读取并查找target，重写拼接section成context，再写入新文件（不变动原来的文件）
def __modify_m21fm(context : list[str],
          new_value: float,
          target : str,
          number_of_occurrences : int):
    first_appear_target_row = -1
    old_target_row = ''
    # 需要修改的目标属性位于n次出现的位置,记录第n次出现位置就行
    count = 0
    for i, line in enumerate(context):
        if target in line:
            count += 1
        if count == number_of_occurrences:
            old_target_row = line
            first_appear_target_row = i
            break
    # 切成2部分: [0]'target'[1]         以target为分界点
    parts = old_target_row.split('= ')
    # 生成新的target
    new_target_row = f'{parts[0]}= {str(new_value)}\n'

    # 拼接成新的m21fm context
    l1 = context[:first_appear_target_row]
    l1.append(new_target_row)
    l2 = context[first_appear_target_row+1:]
    new_m21fm_context = l1 + l2

    return new_m21fm_context

# modify target--->surface_elevation_constant
# modify target--->number_of_time_steps
# modify target--->last_time_step
def gen_m21fm(surface_elevation_constant: float,
              number_of_time_steps: int,
              write_path):

    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    """ 加上预热的1h=360个步长 """
    total_steps = number_of_time_steps + 360
    context = __modify_m21fm(lines, surface_elevation_constant, 'surface_elevation_constant',1)
    context = __modify_m21fm(context, total_steps, 'number_of_time_steps', 1)
    context = __modify_m21fm(context, total_steps, 'last_time_step', 2)
    context = __modify_m21fm(context, total_steps, 'last_time_step', 3)
    context = __modify_m21fm(context, total_steps, 'last_time_step', 4)
    context = __modify_m21fm(context, total_steps, 'last_time_step', 5)
    context = __modify_m21fm(context, total_steps, 'last_time_step', 6)
    with open(write_path, 'w', encoding='utf-8') as f:
        f.writelines(context)


