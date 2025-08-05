
import aspectlib
from aspectlib import Aspect
from src.tools import fill, persistence


@Aspect
def load_and_persistence(*args, **kwargs):
    args = list(args)
    # 加载文件数据并填充入参
    fill(args)
    yield aspectlib.Proceed(*args, **kwargs)
    persistence()

