import os
import orjson
from concurrent.futures import ThreadPoolExecutor, as_completed

import picologging
from tqdm import tqdm
from src.aspect import log_name

__logger = picologging.getLogger(log_name)
def __create_one_case(case, base_path):
    full_path = os.path.join(base_path, case["path"])
    if os.path.isdir(full_path):
        return "skipped"
    try:
        os.makedirs(full_path, exist_ok=True)
        return "created"
    except Exception as e:
        return f"error: {e}"

def gen_case_folder(json_file_path, base_path, max_workers=8):
    try:
        with open(json_file_path, 'rb') as f:
            data = orjson.loads(f.read())
    except Exception as e:
        __logger.error(f"读取 JSON 文件出错: {e}")
        return
    results = {"created": 0, "skipped": 0, "error": 0}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        __logger.info(f"开始创建工况目录层级.....")
        # TODO: 视情况而定
        for case in data['do_nothing_cases']:
            futures.append(executor.submit(__create_one_case, case, base_path))
        for f in tqdm(as_completed(futures), total=len(futures), desc="并发创建工况目录层级中"):
            result = f.result()
            if result == "created":
                results["created"] += 1
            elif result == "skipped":
                results["skipped"] += 1
            else:
                results["error"] += 1
                __logger.error(f"⚠️ 错误: {result}")
    __logger.info(f"✅ 创建成功: {results['created']} 个")
    __logger.info(f"⏭️ 已存在跳过: {results['skipped']} 个")
    __logger.info(f"❌ 出错: {results['error']} 个")
