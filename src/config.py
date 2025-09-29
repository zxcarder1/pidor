from random import getrandbits, randint


# подписываться после дм или перед дм
def FOLLOW_AFTER_DM():
    return not getrandbits(1)

# Подписываться или нет
FOLLOW = False


# таймаут между саб+дм
def TIMEOUT_WORK():
    return randint(5, 10)


# таймаут между кругами
def TIMEOUT_SLEEP():
    return randint(83, 141)
