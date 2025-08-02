import os

import orjson
from tqdm import tqdm
from src.common import script_generated_path
from src.common.enums import StatusEnum


def init_tasks(tasks_json_path,cases_json_path,tasks,cases,manager):
    cases_total = 0
    with open(cases_json_path,'rb') as f:
        cases[:] = orjson.loads(f.read())
        cases_total = len(cases)
    with open(tasks_json_path,'wb') as f:
        tasks_list = []
        for i in tqdm(range(cases_total),desc='初始化任务列表中：'):
            tasks_list.append({"task_id": i, "status": StatusEnum.NOT_STARTED.value})
            tasks.append(manager.dict({"task_id": i, "status": StatusEnum.NOT_STARTED.value}))
        f.write(orjson.dumps(tasks_list,option=orjson.OPT_INDENT_2))

def check_task(task_id : int):
    pass