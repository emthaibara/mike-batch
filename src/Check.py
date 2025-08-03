import os

import orjson
from tqdm import tqdm
from src.common import script_generated_path
from src.common.enums import StatusEnum

tasks_json_path = os.path.join(script_generated_path,'tasks.json')
cases_json_path = os.path.join(script_generated_path,'cases.json')
def init_tasks():
    cases_total = 0
    with open(cases_json_path,'rb') as f:
        raw_cases = orjson.loads(f.read())
        cases_total = len(raw_cases)

    tasks_list = {'tasks': []}
    with open(tasks_json_path,'wb') as f:
        for i in tqdm(range(cases_total),desc='初始化任务列表中：'):
            tasks_list['tasks'].append({"task_id": i, "status": StatusEnum.NOT_STARTED})
        f.write(orjson.dumps(tasks_list))

    return {
            'raw_cases':raw_cases['cases'],
            'raw_tasks':tasks_list['tasks']
            }

task_total = 0
def check_cases():
    if not os.path.exists(cases_json_path):
        raise FileNotFoundError(cases_json_path)
    global task_total
    raw_cases = orjson.loads(open(cases_json_path, 'rb').read())['cases']
    task_total = len(raw_cases)
    print('total cases:',task_total)
    return raw_cases

def check_tasks():
    if not os.path.exists(tasks_json_path):
        tasks_list = {'tasks': []}
        with open(tasks_json_path,'wb') as f:
            for i in tqdm(range(task_total), desc='初始化tasks.json中：'):
                tasks_list['tasks'].append({"task_id": i, "status": StatusEnum.NOT_STARTED})
            f.write(orjson.dumps(tasks_list))
            return tasks_list['tasks']
    else:
        return orjson.loads(open(tasks_json_path,'rb').read())['tasks']
