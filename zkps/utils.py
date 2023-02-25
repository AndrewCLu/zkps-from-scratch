from abc import ABC, abstractmethod

class Byteable(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

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
    