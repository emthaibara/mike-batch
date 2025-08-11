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
    plt.figure(figsize=(10, 6))
    plt.hist(cases_pd['duration'], bins=bins, edgecolor='black')
    plt.xlabel('Duration (hours)')
    plt.ylabel('Number of Cases')
    plt.title(f'[{cases_type}] Case Duration Distribution (0.5h bins)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(os.path.join(__chart_path,f'{cases_type}.png'), dpi=600)
    plt.show()

def __draw_chart():
    df = pd.read_csv(os.path.join(assets_path, 'test', 'z.csv'))
    # 设置时间为索引
    df.set_index('Unnamed: 0', inplace=True)
    # 绘制多条折线
    plt.figure(figsize=(24, 14), dpi=600)
    plt.rcParams['font.sans-serif'] = ['SimHei', 'FangSong', 'STSong', 'Arial Unicode MS', 'Microsoft YaHei',
                                       'Heiti TC', 'WenQuanYi Zen Hei']
    plt.rcParams['axes.unicode_minus'] = False
    for column in df.columns:
        plt.plot(df.index, df[column], label=column)
    plt.xlabel('time', fontsize=14)
    plt.ylabel('elevation (m)', fontsize=14)
    plt.title('不同断面水位变化折线图', fontsize=14)
    plt.grid(True)
    # 旋转日期标签，避免重叠
    plt.xticks(rotation=40, ha='right')
    # 调整图例的位置和列数，使其更清晰
    plt.legend(title='section',
               loc='upper left',
               bbox_to_anchor=(1, 1),
               ncol=1,
               fontsize=10,
               borderaxespad=0.0)
    # 显示图形
    plt.savefig(os.path.join(assets_path, 'test' , 'z.png'), dpi=600)
    plt.show()
