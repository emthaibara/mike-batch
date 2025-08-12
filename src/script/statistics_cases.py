import os
import numpy as np
import orjson
import pandas as pd
from matplotlib import pyplot as plt

from src.common import pump_cases_json_path, generate_electricity_cases_json_path, do_nothing_cases_json_path, \
    script_generated_path, assets_path

__chart_path = os.path.join(script_generated_path,'chart')
if not os.path.exists(__chart_path):
    os.makedirs(__chart_path)
def statistics_cases():
    pump_cases = orjson.loads(open(pump_cases_json_path, 'rb').read())['pump_cases']
    generate_electricity_cases = orjson.loads(open(generate_electricity_cases_json_path, 'rb').read())['gen_cases']
    do_nothing_cases = orjson.loads(open(do_nothing_cases_json_path, 'rb').read())['do_nothing_cases']

    pump_df = pd.DataFrame(pump_cases)
    gen_electric_df = pd.DataFrame(generate_electricity_cases)
    do_nothing_df = pd.DataFrame(do_nothing_cases)

    __draw_duration_distribution(pump_df,'pump',0.5)
    __draw_duration_distribution(gen_electric_df,'generate-electricity',0.5)
    __draw_duration_distribution(do_nothing_df,'do-nothing',0.5)

def __draw_duration_distribution(cases_pd : pd.DataFrame,cases_type : str,bin_width : float):
    min_duration = cases_pd['duration'].min()
    max_duration = cases_pd['duration'].max()
    bins = np.arange(start=min_duration, stop=max_duration + bin_width, step=bin_width)
    # 开始绘图
    plt.figure(figsize=(10, 6),dpi=600)
    plt.hist(cases_pd['duration'], bins=bins, edgecolor='black')
    plt.xlabel('Duration (hours)')
    plt.ylabel('Number of Cases')
    plt.title(f'[{cases_type}] Case Duration Distribution (0.5h bins)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(os.path.join(__chart_path,f'{cases_type}.png'), dpi=600)
    plt.show()


def scatter_plot(file):
    pump_cases = orjson.loads(open(os.path.join(file,'pump_cases.json'), 'rb').read())['pump_cases']
    generate_electricity_cases = orjson.loads(open(os.path.join(file,'gen_cases.json'), 'rb').read())['gen_cases']
    do_nothing_cases = orjson.loads(open(os.path.join(file,'do_nothing_cases.json'), 'rb').read())['do_nothing_cases']

    pump_df = pd.DataFrame(pump_cases)
    gen_electric_df = pd.DataFrame(generate_electricity_cases)
    do_nothing_df = pd.DataFrame(do_nothing_cases)

    __draw_scatter_plot(file, pump_df, 'pump')
    __draw_scatter_plot(file, gen_electric_df, 'generate-electricity')
    __draw_scatter_plot(file, do_nothing_df, 'do-nothing')

def __draw_scatter_plot(file, cases_pd : pd.DataFrame,cases_type : str):
    cases_pd['q1-q3'] = cases_pd['q1-flow_rate'] - cases_pd['q3-flow_rate']
    cases_pd['scaled_duration'] = cases_pd['duration'] * 50
    unique_elevations = cases_pd['elevation'].unique()

    for elevation in unique_elevations:
        # 过滤出当前 elevation 的数据
        df_elev = cases_pd[cases_pd['elevation'] == elevation]
        fig, ax = plt.subplots(figsize=(10, 6), dpi=600)
        # 字体设置
        plt.rcParams['font.sans-serif'] = ['SimHei', 'FangSong', 'STSong', 'Arial Unicode MS', 'Microsoft YaHei',
                                           'Heiti TC', 'WenQuanYi Zen Hei']
        plt.rcParams['axes.unicode_minus'] = False
        df_elev.plot(
            kind='scatter',
            x='q2-flow_rate',
            y='q1-q3',
            s='scaled_duration',  # s参数现在指向 scaled_duration 列
            ax=ax,
            alpha=0.7,  # 设置透明度，以防点重叠
            title=f'elevation = {elevation}'  # 设置图表标题
        )
        plt.xlabel('q2')
        plt.ylabel('q1-q3')
        plt.tight_layout()
        plt.savefig(os.path.join(file, f'{cases_type}_elevation-{elevation}_.png'), dpi=600)
        plt.close(fig)