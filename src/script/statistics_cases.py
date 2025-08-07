import os

import numpy as np
import orjson
import pandas as pd
from matplotlib import pyplot as plt

from src.common import pump_cases_json_path, generate_electricity_cases_json_path, do_nothing_cases_json_path, \
    script_generated_path


def __statistics_cases():
    __pump_cases = orjson.loads(open(pump_cases_json_path, 'rb').read())['cases']
    __generate_electricity_cases = orjson.loads(open(generate_electricity_cases_json_path, 'rb').read())['cases']
    __do_nothing_cases = orjson.loads(open(do_nothing_cases_json_path, 'rb').read())['cases']

    __pump_df = pd.DataFrame(__pump_cases)
    __gen_electric_df = pd.DataFrame(__generate_electricity_cases)
    __do_nothing_df = pd.DataFrame(__do_nothing_cases)

    __draw_duration_distribution(__pump_df,'Pump',0.5)
    __draw_duration_distribution(__gen_electric_df,'Generate electricity',0.5)
    __draw_duration_distribution(__do_nothing_df,'Do nothing',0.5)

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
    plt.savefig(os.path.join(script_generated_path,f'{cases_type}.png'), dpi=500)
    plt.show()

__statistics_cases()