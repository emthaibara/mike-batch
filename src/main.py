import logging

from src.common import setup_logging
from src.script import gen_cases_json


def main():
    """ 生成工况组合并根据计算时常筛选出有效工况 """
    gen_cases_json()
    # """" 根据工况表批量生成工况目录 """
    # gen_case_folder(cases_json_path,simulation_path,max_workers=12)

    # """" 定时同步所有任务状态（每隔10s写入一次tasks.json） """
    # stop_event = threading.Event()
    # thread = threading.Thread(target=start_timing_job,args=(stop_event,))
    # thread.start()
    # """ 开始批量模拟（内容填充前置处理AOP独立出去了，这里传入空列表就行） """
    # start_simulation([],[],stop_event=stop_event)
if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    # 示例日志
    # logger.debug("这是一个调试信息")
    logger.info("This is a test log from other_module")
    for handler in logger.handlers:
        handler.flush()
    # logger.warning("这是一个警告")
    # logger.error("出现了错误")
    # main()
