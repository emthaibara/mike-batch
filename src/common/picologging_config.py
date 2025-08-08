import sys
from datetime import datetime
from pathlib import Path

import picologging
import picologging as logging

from src.common import logs_path

def setup_logging():
    # 设置日志文件路径
    log_dir = Path(logs_path)
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"mike_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # 创建 logger
    logger = picologging.getLogger()
    logger.setLevel(picologging.DEBUG)  # 设置最低级别

    # 创建控制台处理器
    console_handler = picologging.StreamHandler(sys.stdout)
    console_handler.setLevel(picologging.INFO)

    # 控制台格式器
    console_formatter = picologging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)

    # 创建文件处理器
    file_handler = picologging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(picologging.INFO)

    # 文件格式器
    file_formatter = picologging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

