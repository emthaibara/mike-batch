import os

import orjson
from tqdm import tqdm
from src.common import script_generated_path
from src.common.enums import StatusEnum


def init_tasks(tasks_json_path,cases_json_path,tasks,cases,manager):
    cases_total = 0
    with open(cases_json_path,'rb') as f:
        data = orjson.loads(f.read())
        cases[:] = data['cases']
        cases_total = len(cases)
    with open(tasks_json_path,'wb') as f:
        tasks_list = {'tasks':[]}
        for i in tqdm(range(cases_total),desc='初始化任务列表中：'):
            tasks_list['tasks'].append({"task_id": i, "status": StatusEnum.NOT_STARTED})
            tasks.append(manager.dict({"task_id": i, "status": StatusEnum.NOT_STARTED}))
        f.write(orjson.dumps(tasks_list))

def check_task(task_id : int):
    pass