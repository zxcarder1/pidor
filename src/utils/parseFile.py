from typed.Account import Account, Proxy


def parseFile(file: str) -> list[str]:
    with open(file, "r") as f:
        lines = list(filter(len, f.read().replace("\r", "").split("\n")))
        return lines


def parseProfiles(file: str) -> list[str]:
    values = parseFile(file)
    return [value[14:] for value in values]


def parseAccounts(file: str) -> list[Account]:
    values = parseFile(file)
    result: list[Account] = []
    for value in values:
        [proxy, account, user_agent] = value.split("|")

        [login, password] = account.split(":", 5)

        proxy_obj = Proxy.from_string(proxy)

        result.append(
            Account(
                proxy=proxy_obj,
                login=login,
                password=password,
                user_agent=user_agent,
            ),
        )
    return result
