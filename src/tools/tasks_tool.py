import os
from orjson import orjson
from src.common import script_generated_path
from src.enums import StatusEnum

__tasks_json_path = os.path.join(script_generated_path,'tasks.json')
# TODO: 视情况而定
__cases_json_path = os.path.join(script_generated_path,'pump_cases.json')
KEY = 'tasks'
def __load_cases():
    # TODO: 视情况而定
    return orjson.loads(open(__cases_json_path, 'rb').read())['pump_cases']

def __load_tasks():
    return orjson.loads(open(__tasks_json_path, 'rb').read())[KEY]

def __gen_tasks_json(cases):
    with open(__tasks_json_path,'wb') as f:
        tasks = [{'task_id':case['case_id'],
                  'task_status': StatusEnum.not_started}
                      for case in cases]
        f.write(orjson.dumps({KEY:tasks},option=orjson.OPT_INDENT_2))
        return tasks

# 填充 cases、tasks
def fill(cases : list,
         pending_tasks : list,
         cache_tasks : dict):
    __check(cases, pending_tasks, cache_tasks)

def persistence(cache_tasks : dict):
    tasks = []
    for task_id in sorted(cache_tasks.keys()):
        task_status = cache_tasks[task_id]
        tasks.append({'task_id': task_id,'task_status': task_status})
    with open(__tasks_json_path,'wb') as f:
        f.write(orjson.dumps({KEY:tasks}, option=orjson.OPT_INDENT_2))

def __check(cases : list, pending_tasks : list, cache_tasks : dict):
    temp_tasks = list()
    # check cases and load
    if not os.path.exists(__cases_json_path):
        raise FileNotFoundError(__cases_json_path)
    else:
        cases[:] = __load_cases()
    # check tasks and load （要检查cache和json两个位置）
    if not os.path.exists(__tasks_json_path):
        temp_tasks[:] = __gen_tasks_json(cases)

    temp_tasks[:] = __load_tasks()

    for task in temp_tasks:
        cache_tasks[task['task_id']] = task['task_status']
        if task['task_status'] != StatusEnum.completed.value:
            pending_tasks.append(task['task_id'])
