from enum import Enum,auto

class StatusEnum(Enum):
    completed  = '已完成任务'
    error = '任务执行异常'
    in_process  = '模拟任务进行中'
    not_started  = '未开始模拟任务'


