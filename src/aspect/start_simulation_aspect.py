
import aspectlib
from aspectlib import Aspect
from src.tools import fill, persistence


@Aspect
def load_and_persistence(*args, **kwargs):
    args = list(args)
    kwargs = dict(kwargs)
    # 加载文件数据并填充入参
    fill(args)
    yield aspectlib.Proceed(*args, **kwargs)
    # 持久化任务状态
    persistence()

