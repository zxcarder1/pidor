from __future__ import annotations

from urllib.parse import urlsplit


class Proxy:
    scheme: str
    login: str
    password: str
    ip: str
    port: int

    def __init__(
        self,
        ip: str,
        port: int,
        login: str,
        password: str,
        scheme: str = "http",
    ) -> None:
        self.scheme = scheme or "http"
        self.login = login
        self.password = password
        self.ip = ip
        self.port = int(port)

    @classmethod
    def from_string(cls, raw_proxy: str) -> "Proxy":
        value = raw_proxy.strip()

        if not value:
            raise ValueError("Proxy value is empty")

        if "://" in value:
            parsed = urlsplit(value)

            if parsed.hostname is None or parsed.port is None:
                raise ValueError(f"Proxy url '{value}' is missing host or port")

            return cls(
                ip=parsed.hostname,
                port=parsed.port,
                login=parsed.username or "",
                password=parsed.password or "",
                scheme=parsed.scheme or "http",
            )

        parts = value.split(":")

        if len(parts) != 4:
            raise ValueError(
                "Proxy must be in 'ip:port:login:password' or 'scheme://login:password@ip:port' format",
            )

        ip, port, login, password = parts

        return cls(ip=ip, port=int(port), login=login, password=password, scheme="http")

    @property
    def url(self) -> str:
        auth = f"{self.login}:{self.password}@" if self.login else ""
        return f"{self.scheme}://{auth}{self.ip}:{self.port}"


class Account:
    proxy: Proxy
    login: str
    password: str
    user_agent: str

    def __init__(
        self, proxy: Proxy, login: str, password: str, user_agent: str
    ) -> None:
        self.proxy = proxy
        self.login = login
        self.password = password
        self.user_agent = user_agent
