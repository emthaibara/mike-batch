from dataclasses import dataclass
from src.enums import StatusEnum

@dataclass
class TaskEntity:
    task_id: int
    task_status: StatusEnum
    task_info: dict
