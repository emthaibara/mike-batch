import threading
import time
import picologging
from src.aspect import log_name
from src.enums import StatusEnum
from src.tools import persistence

__is_completed = False
__logger = picologging.getLogger(log_name)
def __store_tasks_job():
    cached_tasks = persistence(True)
    if all(int(task[1]) == StatusEnum.completed.value for task in cached_tasks.items()):
        global __is_completed
        __is_completed = True
        __logger.info('all task completed !')
    else:
        persistence(False)
        __logger.info('定时同步所有模拟任务状态 cache tasks -------> tasks.json store successfully !')

def start_timing_job(stop_event: threading.Event):
    while not __is_completed:
        time.sleep(5)
        __store_tasks_job()
        if stop_event.is_set():
            break