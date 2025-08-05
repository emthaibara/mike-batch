import aspectlib
import redis
from aspectlib import Aspect

from src.enums import StatusEnum
from src.tools import KEY

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
@Aspect
def update_task_status(*args, **kwargs):
    # 任务状态设置为进行中⛔️
    task_id = args[0]
    r.hset(KEY,str(task_id),str(StatusEnum.in_process.value))
    yield aspectlib.Proceed(*args, **kwargs)
    # 任务状态设置为已完成✅
    r.hset(KEY, str(task_id), str(StatusEnum.completed.value))