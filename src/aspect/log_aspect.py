import os
from datetime import datetime

import aspectlib
import picologging
from aspectlib import Aspect

from src.common import logs_path

log_name = "mike-batch-script"

# ANSI 颜色常量
class AnsiColors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'  # 重置所有颜色和样式

# --- 自定义带颜色的 Formatter ---
class ColoredFormatter(picologging.Formatter):
    """
    一个用于为控制台日志消息添加颜色的 Formatter。
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        # 定义不同日志级别的颜色映射
        self.level_colors = {
            picologging.DEBUG: AnsiColors.CYAN,
            picologging.INFO: AnsiColors.GREEN,
            picologging.WARNING: AnsiColors.YELLOW,
            picologging.ERROR: AnsiColors.RED,
            picologging.CRITICAL: AnsiColors.MAGENTA,
        }
    def format(self, record):
        # 根据日志级别获取颜色代码
        color = self.level_colors.get(record.levelno, AnsiColors.WHITE)
        # 调用父类的 format 方法来获取格式化后的消息
        message = super().format(record)
        # 在消息前后添加颜色代码
        return f"{color}{message}{AnsiColors.RESET}"

@Aspect
def init_picologging(*args, **kwargs):
    init_logging()
    yield aspectlib.Proceed(*args, **kwargs)

def init_logging():
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    logger = picologging.getLogger(log_name)
    log_file_path = os.path.join(logs_path, f"mike-batch-all.log")
    file_formatter = picologging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = picologging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    # 4. 创建控制台处理器 (StreamHandler)
    console_handler = picologging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # 5. 将处理器添加到 logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 设置日志级别
    logger.setLevel(picologging.INFO)


