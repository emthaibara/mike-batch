import os

work_space_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
assets_path = os.path.join(work_space_path, 'assets')
script_generated_path = os.path.join(assets_path, 'generated')
cases_json_path = os.path.join(script_generated_path, 'cases.json')
pump_cases_json_path = os.path.join(script_generated_path, 'pump_cases.json')
generate_electricity_cases_json_path = os.path.join(script_generated_path, 'gen_cases.json')
do_nothing_cases_json_path = os.path.join(script_generated_path, 'do_nothing_cases.json')
simulation_path = os.path.join(script_generated_path, 'simulation')
required_path = os.path.join(assets_path, 'required')
z0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'z0_cases.csv')
v0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'v0_cases.csv')
logs_path = os.path.join(work_space_path, 'logs')
origin_m21fm_path = os.path.join(required_path, 'LHKHX.m21fm')
dfsu_path = os.path.join(required_path, 'Manning.dfsu')
mesh_path = os.path.join(required_path, 'LHKHX.mesh')
FemEngine_location = r'C:\Program Files (x86)\DHI\2014\bin\x64\FemEngineHD.exe'