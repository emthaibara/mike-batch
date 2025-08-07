import os

import orjson
import redis
from tqdm import tqdm
from src.common import script_generated_path
from src.enums import StatusEnum

__tasks_json_path = os.path.join(script_generated_path,'tasks.json')
__cases_json_path = os.path.join(script_generated_path,'cases.json')
__rd = redis.Redis(host='localhost', port=6379, decode_responses=True)
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
                      for i in tqdm(range(__task_total),
                                    desc='tasks.json not exist, generating tasks json')]
        f.write(orjson.dumps({KEY:__tasks},option=orjson.OPT_INDENT_2))

# 填充 cases、tasks
def fill(args):
    __check()
    args[0] = __cases
    args[1] = __filter_tasks()

def persistence(is_return=False):
    cached_tasks = __rd.hgetall(KEY)
    if is_return:
        return cached_tasks
    else:
        tasks_json = {KEY:[]}
        for task in cached_tasks.items():
            tasks_json[KEY].append({'task_id': int(task[0]), 'task_status': int(task[1])})
        with open(__tasks_json_path,'wb') as f:
            f.write(orjson.dumps(tasks_json))
            return None

# 任务筛选，如果该任务状态未完成则
def __filter_tasks():
    pending_tasks = []
    for task in __tasks:
        if task['task_status'] != StatusEnum.completed.value:
            pending_tasks.append(task['task_id'])
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
    # 由于任务数量较多，可以用redis的管道来减少io次数，io实际上只发生一次，类似打包
    pipe = __rd.pipeline()
    for task_id in tqdm(range(__task_total),
                        desc='batch write using pipeline to caching tasks'):
        pipe.hset(KEY, str(task_id), str(StatusEnum.not_started.value))
    pipe.execute()


if __name__ == '__main__':
    __task_total = 84374
    __init_tasks_cache()
    __rd.delete(KEY)