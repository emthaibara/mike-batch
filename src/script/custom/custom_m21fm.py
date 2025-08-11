from src.common import origin_m21fm_path

# 格式化m21fm：去掉所有空行，紧凑布局
def __format_m21fm():
    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(origin_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)
# __format_m21fm()

""" 原地修改内容 """
def __modify_m21fm_in_place(context: list[str],
                             new_value: float,
                             target: str,
                             number_of_occurrences: int) -> None: # 目标字符串位于第几次出现的位置
    count = 0
    for i, line in enumerate(context):
        if target in line:
            count += 1
        if count == number_of_occurrences:
            old_target_row = line
            parts = old_target_row.split('= ')
            new_target_row = f'{parts[0]}= {str(new_value)}\n'
            context[i] = new_target_row  # 直接原地修改
            break

""" 只读取一次原始配置文件内容 """
__origin_context = open(origin_m21fm_path, 'r', encoding='utf-8').readlines()
def gen_m21fm(surface_elevation_constant: float,
              number_of_time_steps: int,
              write_path):
    """ 复制一份原始配置文件内容 """
    context = __origin_context[:]
    """ 修改高程、总步长 """
    total_steps = number_of_time_steps + 360
    __modify_m21fm_in_place(context,surface_elevation_constant, 'surface_elevation_constant',1)
    __modify_m21fm_in_place(context, total_steps,'number_of_time_steps', 1)
    """ 修改所有输出文件的步长 """
    for i in range(2, 7):
        __modify_m21fm_in_place(context,total_steps,'last_time_step', i)

    with open(write_path, 'w', encoding='utf-8') as f:
        f.writelines(context)

