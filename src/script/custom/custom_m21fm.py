import os.path
from src.common import assets_path, origin_m21fm_path


# 格式化m21fm：去掉所有空行，紧凑布局
def __format_m21fm():
    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(origin_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)
# __format_m21fm()

# 逐行读取并查找target，重写拼接section成context，再写入新文件（不变动原来的文件）
def __gen(context : list[str],
          new_value: float,
          target : str):
    first_appear_target_row = -1
    old_target_row = ''
    # 需要修改的目标属性位于首次出现的位置,记录第一次出现位置就行
    for i, line in enumerate(context):
        if target in line:
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

# target---surface_elevation_constant
# target---number_of_time_steps
def gen_m21fm(surface_elevation_constant: float,
              number_of_time_steps: int,
              write_path):

    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    context = __gen(lines, surface_elevation_constant, 'surface_elevation_constant')
    modified_context = __gen(context, number_of_time_steps, 'number_of_time_steps')

    with open(os.path.join(write_path,'LHKHK.m21fm'), 'w', encoding='utf-8') as f:
        f.writelines(modified_context)
