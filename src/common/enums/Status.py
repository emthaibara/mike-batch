from enum import Enum,auto

class StatusEnum(Enum):
    COMPLETED  = auto() # 1
    ERROR = auto() # 2
    IN_PROGRESS  = auto() # 3
    NOT_STARTED  = auto() # 4


