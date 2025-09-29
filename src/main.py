import asyncio
from os import makedirs

from utils import parseAccounts, parseFile, parseProfiles, Worker, AtomicInteger, Log
from twikit import errors

makedirs("./sessions", exist_ok=True)

accounts = parseAccounts("accounts.txt")
texts = parseFile("texts.txt")
profiles = parseProfiles("profiles.txt")


async def work(worker: Worker, profile: str, text: str):
    return await worker.work(profile, text)


def wrapper(coro):
    return asyncio.run(coro)


async def main():
    workers: list[Worker] = []

    for account in accounts:
        print(f"[{account.login}]: Захожу в аккаунт")

        errorCount = 0
        while errorCount != 3:
            try:
                workers.append(await Worker(account).auth())
                print(f"[{account.login}]: Вход завершен")
                break
            except errors.NotFound:
                print(f"[{account.login}]: 404 Ошибка входа")
                errorCount +=1
        else:
            return
        

    log = Log()
    result = (AtomicInteger(), AtomicInteger())

    current_text = 0
    current_worker = 0

    tasks = []

    for profile in profiles:
        worker = workers[current_worker]
        text = texts[current_text]

        tasks.append(asyncio.create_task(worker.work(profile, text, log, result)))

        current_worker += 1
        if not current_worker % len(workers):
            current_text += 1
            current_worker = 0

        if current_text == len(texts):
            current_text = 0

    await asyncio.gather(*tasks)

    await log.result(
        f"Всего отправлено: {result[0].value}\tНе отправлено: {result[1].value}"
    )


asyncio.run(main())
