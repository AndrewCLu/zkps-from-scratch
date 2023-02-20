from typing import Generic, List, Optional, Type
from algebra import FElt
from Crypto.Hash import keccak

class Transcript(Generic[FElt]):
    def __init__(self, field_class: Type[FElt]) -> None:
        self.field_class: Type[FElt] = field_class
        self.record: bytearray = bytearray()

    def append(self, entry: bytes) -> None:
        self.record.extend(entry)

    def get_hash(self, salt: Optional[bytes]) -> FElt:
        bytes_copy = self.record[:]
        if salt:
            bytes_copy.extend(salt)
        k = keccak.new(digest_bits=256)
        k.update(bytes_copy)

        return self.field_class(int(k.hexdigest(), 16))
