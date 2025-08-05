import os.path
from src.common import assets_path

m21fm_path = os.path.join(assets_path, 'required', 'LHKHX.m21fm')
format_m21fm_path = os.path.join(assets_path, 'test', 'Script-gen-LHKHX.m21fm')
# 格式化m21fm：去掉所有空行，紧凑布局
def format_m21fm():
    with open(m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)
format_m21fm()

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
    # 切成2部分: [0]'target'[1]         以target为分界点
    parts = old_target_row.split('= ')
    # 生成新的target
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


