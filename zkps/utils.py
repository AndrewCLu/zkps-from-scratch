from abc import ABC, abstractmethod

class Byteable(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

def unsigned_int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
def unsigned_int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

def is_power_of_2(n: int) -> bool:
    curr = 1
    while True:
        if curr == n:
            return True
        if curr > n:
            return False
        curr *= 2
    
def get_smallest_power_of_2_greater_than_n(n: int) -> int:
    curr = 1
    while curr < n:
        curr *= 2
    
    return curr
