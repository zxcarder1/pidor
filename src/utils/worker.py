import os
from asyncio import Lock, sleep
from httpx import AsyncHTTPTransport, Timeout
from httpx._utils import URLPattern
from httpx_socks import AsyncProxyTransport
from twikit import Client
from config import FOLLOW, FOLLOW_AFTER_DM, TIMEOUT_SLEEP, TIMEOUT_WORK
from typed.Account import Account
from twikit import errors

from utils.atomic import AtomicInteger
from utils.output import Log


class Worker:
    _client: Client
    account: Account
    _lock: Lock
    _skip: bool

    def __init__(self, account: Account) -> None:
        transport = AsyncHTTPTransport(retries=3)
        proxy_url: str | None = account.proxy.url

        if account.proxy.scheme.lower().startswith("socks"):
            transport = AsyncProxyTransport.from_url(account.proxy.url)
            proxy_url = None

        client = Client(
            language="en-US",
            proxy=proxy_url,
            user_agent=account.user_agent,
            transport=transport,
            verify=False,
            timeout=Timeout(30.0, connect=30),
        )
        self._client = client

        if isinstance(transport, AsyncProxyTransport):
            client.http._transport = transport
            client.http._mounts = {URLPattern("all://"): transport}
        self.account = account
        self._lock = Lock()
        self._skip = False

    async def auth(self):
        session_path = f"./sessions/{self.account.login}.json"

        if os.path.exists(session_path):
            self._client.load_cookies(session_path)

        try:
            await self._client.user_id()
        except errors.Unauthorized:
            await self._client.login(
                auth_info_1=self.account.login,
                password=self.account.password,
            )
        except errors.AccountLocked:
            print(f"[{self.account.login}]: Аккаунт локнут")

        self._client.save_cookies(session_path)

        return self

    async def work(
        self,
        profile: str,
        text: str,
        log: Log,
        result: tuple[AtomicInteger, AtomicInteger],
    ):
        await self._lock.acquire()

        form = f"{self.account.login} {profile}"

        if self._skip:
            await log.error(form, "Скипаю оставшиеся профиля...")

            await log.writeErrorAccs(profile)

            result[1].inc()

            self._lock.release()
            return self

        try:
            user = await self._client.get_user_by_screen_name(profile)

            followAfterDm = FOLLOW_AFTER_DM()

            if followAfterDm:
                await self._client.send_dm(user.id, text)
                await log.result(form, "Сообщение отправлено")

                await sleep(TIMEOUT_WORK())

                if FOLLOW:
                    await self._client.follow_user(user.id)
                    await log.result(form, "Подписался")
            else:
                if FOLLOW:
                    await self._client.follow_user(user.id)
                    await log.result(form, "Подписался")

                await sleep(TIMEOUT_WORK())

                await self._client.send_dm(user.id, text)
                await log.result(form, "Сообщение отправлено")

            result[0].inc()

        except (
            errors.AccountSuspended,
            errors.Unauthorized,
            errors.AccountLocked,
        ) as err:
            await log.error(form, str(err), "Скипаю оставшиеся профиля...")
            await log.writeErrorAccs(profile)
            self._skip = True
            result[1].inc()

        except Exception as err:
            await log.error(form, str(err))
            await log.writeErrorAccs(profile)
            result[1].inc()

        await sleep(TIMEOUT_SLEEP())

        self._lock.release()
        return self
