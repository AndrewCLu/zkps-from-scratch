from typing import Generic, List, Optional, Type
from algebra.field import FElt
from Crypto.Hash import keccak
from utils import Byteable

class Transcript(Generic[FElt]):
    def __init__(self, field_class: Type[FElt]) -> None:
        self.field_class: Type[FElt] = field_class
        self.record: bytearray = bytearray()

    def append(self, entry: Byteable) -> None:
        self.record.extend(entry.to_bytes())
        print("Appending {s} to transcript...".format(s=str(entry)))

    def get_hash(self, salt: Optional[bytes]=None) -> FElt:
        bytes_copy = self.record[:]
        if salt:
            bytes_copy.extend(salt)
        k = keccak.new(digest_bits=256)
        k.update(bytes_copy)

        hash_int = int(k.hexdigest(), 16)
        print("Produced hash {s} from transcript...".format(s=str(hash_int)))
        return self.field_class(hash_int)
