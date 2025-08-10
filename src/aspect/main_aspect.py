import os
import time

import aspectlib
import picologging
from aspectlib import Aspect
from src.aspect import log_name
from src.common import script_generated_path, cases_json_path, simulation_path
from src.script.gen_case_folder import gen_case_folder

__logger = picologging.getLogger(log_name)
@Aspect
def check(*args, **kwargs):
    __logger.info('正在运行前检查工况表以及对应的工况目录层级是否存在⏳')
    time.sleep(3)
    if not os.path.exists(script_generated_path):
        __logger.info('后续脚本生成的文件及文件夹的顶层目录【generated】不存在正在创建⏳')
        time.sleep(3)
        os.makedirs(script_generated_path)
        __logger.info('后续脚本生成的文件及文件夹的顶层目【generated】创建成功✅')
    if not os.path.exists(cases_json_path):
        """ 生成工况组合并根据计算时常筛选出有效工况 """
        __logger.info('工况表不存在,正在生成中⏳')
        time.sleep(3)
        from src.script import gen_cases_json
        gen_cases_json()
        __logger.info('工况表生成成功✅')
    else:
        __logger.info('工况表已存在✅')

    if not os.path.exists(simulation_path):
        """" 根据工况表批量生成工况目录 """
        __logger.info('所有工况对应的目录层级不存在,正在生成中⏳')
        gen_case_folder(cases_json_path,simulation_path,max_workers=12)
        __logger.info('所有工况对应的目录层级生成成功✅')
    else:
        __logger.info('所有工况对应的目录层级已存在✅')
    time.sleep(2)
    __logger.info('运行前检查完毕✅')
    yield aspectlib.Proceed(*args, **kwargs)
