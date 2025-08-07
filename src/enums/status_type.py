from enum import Enum,auto

class StatusEnum(Enum):
    completed  = auto()
    error = auto()
    in_process  = auto()
    not_started  = auto()


