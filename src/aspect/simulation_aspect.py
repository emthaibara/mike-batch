import aspectlib
from aspectlib import Aspect


@Aspect
def load_and_persistence(*args, **kwargs):

    yield aspectlib.Proceed(*args, **kwargs)
