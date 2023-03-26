from abc import ABC, abstractmethod


class Byteable(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass


def unsigned_int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, "big")


def unsigned_int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, "big")


# Returns -1 if n is not a power of 2
def get_power_of_2(n: int) -> int:
    curr = 1
    power = 0
    while True:
        if curr == n:
            return power
        if curr > n:
            return -1
        curr *= 2
        power += 1


def nearest_larger_power_of_2(n: int) -> int:
    curr = 1
    while curr < n:
        curr *= 2

    return curr
