import argparse
import sys
from src.script import gen_cas_json

""" 定义参数解析函数 """
def __check_parse_args():
    parser = argparse.ArgumentParser(description="启动主程序前需要传入一些参数:")
    # parser.add_argument('--script_output_path', type=str, help="您希望脚本生成的文件/文件夹的所在位置")
    parser.add_argument('--z0_cases_count', type=int, help="请输入[初始水位]的工况数量")
    parser.add_argument('--q1_cases_count', type=int, help="请输入[两河口流量]的工况数量")
    parser.add_argument('--q2_cases_count', type=int, help="请输入[混蓄抽水/发电流量]的工况数量")
    parser.add_argument('--q3_cases_count', type=int, help="请输入[牙根一级流量]的工况数量")
    args = parser.parse_args()
    if any(arg <= 0 for arg in [args.z0_cases_count, args.q1_cases_count,
                                args.q2_cases_count, args.q3_cases_count]):
        print("错误：所有工况数量参数都必须是大于0的整数！")
        sys.exit(1)
    return args

def main():
    """ 启动前入参检查 """
    args = __check_parse_args()
    z0_cases_count = args.z0_cases_count
    q1_cases_count = args.q1_cases_count
    q2_cases_count = args.q2_cases_count
    q3_cases_count = args.q3_cases_count
    """ 生成工况组合并根据计算时常筛选出有效工况 """
    gen_cas_json(z0_cases_count, q1_cases_count, q2_cases_count, q3_cases_count)
    # """" 根据工况表批量生成工况目录 """
    # gen_case_folder(cases_json_path,simulation_path,max_workers=12)

    # """" 定时同步所有任务状态（每隔10s写入一次tasks.json） """
    # stop_event = threading.Event()
    # thread = threading.Thread(target=start_timing_job,args=(stop_event,))
    # thread.start()
    # """ 开始批量模拟（内容填充前置处理AOP独立出去了，这里传入空列表就行） """
    # start_simulation([],[],stop_event=stop_event)

if __name__ == '__main__':
    main()
