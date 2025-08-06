import os

work_space_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

assets_path = os.path.join(work_space_path, 'assets')
script_generated_path = os.path.join(assets_path, 'generated')
cases_json_path = os.path.join(script_generated_path, 'cases.json')
simulation_path = os.path.join(script_generated_path, 'simulation')
q1_cases_path = os.path.join(work_space_path, 'assets', 'required', 'q1_cases.csv')
q2_cases_path = os.path.join(work_space_path, 'assets', 'required', 'q2_cases.csv')
q3_cases_path = os.path.join(work_space_path, 'assets', 'required', 'q3_cases.csv')
z0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'z0_cases.csv')
v0_cases_path = os.path.join(work_space_path, 'assets', 'required', 'v0_cases.csv')

