import threading
import time
from datetime import datetime

from colorama import Fore
from tqdm import tqdm

from src.enums import StatusEnum
from src.tools import persistence

__is_completed = False
def __store_tasks_job():
    cached_tasks = persistence(True)
    if all(int(task[1]) == StatusEnum.completed.value for task in cached_tasks.items()):
        global __is_completed
        __is_completed = True
        tqdm.write(f'{Fore.GREEN}{datetime.now()}: all task completed !')
    else:
        persistence(False)
        tqdm.write(f'{Fore.GREEN}{datetime.now()}: 定时同步所有模拟任务状态 cache tasks -------> tasks.json store successfully !')

def start_timing_job(stop_event: threading.Event):
    while not __is_completed:
        time.sleep(5)
        __store_tasks_job()
        if stop_event.is_set():
            break