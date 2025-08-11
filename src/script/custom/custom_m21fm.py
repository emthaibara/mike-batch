import os
from multiprocessing import Pool

from src.common import assets_path, origin_m21fm_path

# 格式化m21fm：去掉所有空行，紧凑布局
def __format_m21fm():
    with open(origin_m21fm_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_section = [line for line in lines if line.strip() != '']
    with open(origin_m21fm_path, 'w', encoding='utf-8') as f:
        f.writelines(new_section)
__format_m21fm()

# 优化后的修改函数，直接在原地修改列表
def __modify_m21fm_in_place(context: list[str],
                             new_value: float,
                             target: str,
                             number_of_occurrences: int) -> None:
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

__origin_context = open(origin_m21fm_path, 'r', encoding='utf-8').readlines()
def gen_m21fm(surface_elevation_constant: float,
              number_of_time_steps: int,
              write_path):
    """ 加上预热的1h=360个步长 """
    context = __origin_context[:]
    total_steps = number_of_time_steps + 360
    __modify_m21fm_in_place(context,surface_elevation_constant, 'surface_elevation_constant',1)
    __modify_m21fm_in_place(context, total_steps,'number_of_time_steps', 1)
    # 循环处理 last_time_step，代码更简洁
    for i in range(2, 7):
        __modify_m21fm_in_place(context,total_steps,'last_time_step', i)

    with open(write_path, 'w', encoding='utf-8') as f:
        f.writelines(context)

if __name__ == '__main__':
    tasks = []
    for index in range(10):
        steps = 500 + index
        surface_elevation = 1.0 + index * 0.1
        wp = os.path.join(assets_path, 'test', f'case_{index}.m21fm')
        tasks.append((surface_elevation, steps, wp))

    # 3. 创建并启动进程池，并发执行 10 个任务
    print("开始并发执行 10 个进程...")
    with Pool(processes=10) as pool:
        pool.starmap(gen_m21fm, tasks)

