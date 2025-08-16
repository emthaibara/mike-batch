from enum import Enum,auto

class StatusEnum(Enum):
    completed  = '已完成'
    error = '任务执行异常'
    in_process  = '模拟进行中'
    not_started  = '未开始'


