from asyncio import Lock
from datetime import datetime
from io import TextIOWrapper
from os import makedirs


class Log:
    _resultFile: str
    _errorFile: str
    _errorAccsFile: str
    _lock: Lock

    def __init__(self) -> None:
        makedirs("./output", exist_ok=True)

        now = datetime.now().strftime("%d-%m-%Y %H-%M-%S")

        reusltFileName = f"{now} - result.txt"
        errorFileName = f"{now} - error.txt"
        errorAccsFileName = f"{now} - errorAccs.txt"

        self._resultFile = rf".\output\{reusltFileName}"
        self._errorFile = rf".\output\{errorFileName}"
        self._errorAccsFile = rf".\output\{errorAccsFileName}"

        self._lock = Lock()

    async def result(self, *text) -> None:
        await self._lock.acquire()

        output = " ".join([datetime.now().strftime("%d-%m-%Y %H-%M-%S"), *text])

        with open(self._resultFile, "a+", encoding="UTF-8") as f:
            f.write(output + "\n")

        print(output)

        self._lock.release()

    async def error(self, *text) -> None:
        await self._lock.acquire()

        output = " ".join([datetime.now().strftime("%d-%m-%Y %H-%M-%S"), *text])

        with  open(self._errorFile, "a+", encoding="UTF-8") as f:
            f.write(output + "\n")

        print(output)

        self._lock.release()

    async def writeErrorAccs(self, account: str) -> None:
        await self._lock.acquire()

        with open(self._errorAccsFile, "a+", encoding="UTF-8") as f:
            f.write(f"https://x.com/{account}" + "\n")

        self._lock.release()
