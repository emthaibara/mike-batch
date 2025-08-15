import os

import redis
from orjson import orjson
from src.common import script_generated_path, rd_host, rd_port
from src.enums import StatusEnum

__tasks_json_path = os.path.join(script_generated_path,'tasks.json')
__cases_json_path = os.path.join(script_generated_path,'cases.json')
__rd = redis.Redis(host=rd_host, port=rd_port, decode_responses=True)
__task_total = int()
__cases = list()
__tasks = list()
KEY = 'tasks'
def __load_cases():
    global __task_total
    global __cases
    __cases[:] = orjson.loads(open(__cases_json_path, 'rb').read())['cases']
    __task_total = len(__cases)

def __load_tasks():
    global __tasks
    __tasks[:] = orjson.loads(open(__tasks_json_path, 'rb').read())[KEY]

def __gen_tasks_json():
    global __tasks
    with open(__tasks_json_path,'wb') as f:
        __tasks[:] = [{'task_id':i,'task_status': StatusEnum.not_started}
                      for i in range(__task_total)]
        f.write(orjson.dumps({KEY:__tasks},option=orjson.OPT_INDENT_2))

# 填充 cases、tasks
def fill(args):
    __check()
    args[0] = __cases
    args[1] = __filter_tasks()

def persistence(is_return=False):
    cached_tasks = __rd.hgetall(KEY)
    sorted_items = sorted(cached_tasks.items(), key=lambda item: int(item[0]))
    if is_return:
        return sorted_items
    else:
        tasks_json = {KEY:[]}
        for task in sorted_items:
            tasks_json[KEY].append({'task_id': int(task[0]), 'task_status': task[1]})
        with open(__tasks_json_path,'wb') as f:
            f.write(orjson.dumps(tasks_json,option=orjson.OPT_INDENT_2))
            return None

# 任务筛选，如果该任务状态未完成则进入就绪状态
def __filter_tasks():
    pending_tasks = []
    pipe = __rd.pipeline()
    for task in __tasks:
        if task['task_status'] != StatusEnum.completed.value:
            __rd.hset(KEY, task['task_id'], StatusEnum.pending.value)
            pending_tasks.append(task['task_id'])
    pipe.execute()
    return pending_tasks

def __check():
    # check cases and load
    if not os.path.exists(__cases_json_path):
        raise FileNotFoundError(__cases_json_path)
    else:
        __load_cases()

    # check tasks and load （要检查cache和json两个位置）
    if not os.path.exists(__tasks_json_path):
        __check_tasks_cache()
        __gen_tasks_json()

    __load_tasks()

def __check_tasks_cache():
    if not __rd.exists(KEY):
        __init_tasks_cache()

def __init_tasks_cache():
    pipe = __rd.pipeline()
    for task_id in range(__task_total):
        pipe.hset(KEY, str(task_id), str(StatusEnum.not_started.value))
    pipe.execute()

def fresh_cache_tasks():
    cached_tasks = __rd.hgetall(KEY)
    pipe = __rd.pipeline()
    for task in cached_tasks.items():
        if task[1] == StatusEnum.in_process.value:
            pipe.hset(KEY, task[0], str(StatusEnum.not_started.value))
    pipe.execute()
