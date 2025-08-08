import os

work_space_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
assets_path = os.path.join(work_space_path, 'assets')
script_generated_path = os.path.join(assets_path, 'generated')
if not os.path.exists(script_generated_path):
    os.makedirs(script_generated_path)
cases_json_path = os.path.join(script_generated_path, 'cases.json')
pump_cases_json_path = os.path.join(script_generated_path, 'pump_cases.json')
generate_electricity_cases_json_path = os.path.join(script_generated_path, 'gen_cases.json')
do_nothing_cases_json_path = os.path.join(script_generated_path, 'do_nothing_cases.json')
simulation_path = os.path.join(script_generated_path, 'simulation')
required_path = os.path.join(assets_path, 'required')
z0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'z0_cases.csv')
v0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'v0_cases.csv')
logs_path = os.path.join(work_space_path, 'logs')
