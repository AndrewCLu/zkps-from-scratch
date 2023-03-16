from typing import Generic, List, Type, Tuple, Any, Union, overload
from dataclasses import dataclass
from algebra import FElt, CyclicGroupElt, Polynomial
from polynomial_commitment_schemes.pcs import Commitment, Opening, PCSProver, PCSVerifier
from utils import nearest_larger_power_of_2, get_power_of_2
from transcript import Transcript

@dataclass
class BulletproofsCRS(Generic[FElt, CyclicGroupElt]):
    G_elts: List[CyclicGroupElt]
    H: CyclicGroupElt

    @staticmethod
    # This is not secure since we are generating detrerministically 
    def common_setup(d: int, cyclic_group: Type[CyclicGroupElt]) -> 'BulletproofsCRS':
        G_elts = []
        g = cyclic_group.generator()
        for i in range(d):
            G_elts.append(g * i)
        H = g * d

        return BulletproofsCRS(
            G_elts=G_elts,
            H=H
        )

@dataclass
class BulletproofsCommitment(Commitment, Generic[CyclicGroupElt]):
    value: CyclicGroupElt

    def to_bytes(self) -> bytes:
        return self.value.to_bytes()

@dataclass
class BulletproofsOpeningProof(Generic[FElt, CyclicGroupElt]):
    L_js: List[CyclicGroupElt]
    R_js: List[CyclicGroupElt]
    R: CyclicGroupElt
    z_1: FElt
    z_2: FElt
    
@dataclass
class BulletproofsOpening(Opening, Generic[FElt, CyclicGroupElt]):
    value: BulletproofsOpeningProof

class BulletproofsProver(PCSProver, Generic[FElt, CyclicGroupElt]):
    def __init__(self, crs: BulletproofsCRS, field_class: Type[FElt]):
        self.crs: BulletproofsCRS = crs
        self.field_class: Type[FElt] = field_class
        self.r: FElt = self.field_class(1234) # Fix randomness for consistent testing 

    # TODO: Better algorithms for MSM    
    def __multiScalarMultiplication(self, scalars: List[FElt], groupElts: List[CyclicGroupElt]) -> CyclicGroupElt:
        if len(scalars) != len(groupElts):
            raise Exception('Length of scalars must be the same as those of group elements!')

        res = groupElts[0].identity() # TODO: Remove class reference from instance
        for i in range(len(scalars)):
            res += groupElts[i] * scalars[i].n
        
        return res

    def __scalarDotProduct(self, a: List[FElt], b: List[FElt]) -> FElt:
        if len(a) != len(b):
            raise Exception('Length of both scalar vectors must be the same!')

        res = self.field_class.zero() 
        for i in range(len(a)):
            res += a[i] * b[i]
        
        return res

    def __split_lo_hi(self, vec: List[Any]) -> Tuple[List[Any], List[Any]]:
        if len(vec) % 2 != 0:
            raise Exception('Cannot split vector of odd length!')
        return (vec[:len(vec) // 2], vec[len(vec) // 2:])

    @overload
    def __scale_vec(self, vec: List[FElt], scalar: FElt) -> List[FElt]:
        ...
    
    @overload
    def __scale_vec(self, vec: List[CyclicGroupElt], scalar: FElt) -> List[CyclicGroupElt]:
        ...

    def __scale_vec(self, vec: Union[List[FElt], List[CyclicGroupElt]], scalar: FElt) -> Union[List[FElt], List[CyclicGroupElt]]:
        res = []
        for i in range(len(vec)):
            res.append(vec[i] * scalar)

        return res
    
    @overload
    def __add_vec(self, a: List[FElt], b: List[FElt]) -> List[FElt]:
        ...

    @overload
    def __add_vec(self, a: List[CyclicGroupElt], b: List[CyclicGroupElt]) -> List[CyclicGroupElt]:
        ...
 
    # TODO: Can have better type annotations for return value
    def __add_vec(self, a: Union[List[FElt], List[CyclicGroupElt]], b: Union[List[FElt], List[CyclicGroupElt]]) -> List[Any]:
        res = []
        for i in range(len(a)):
            res.append(a[i] + b[i])
        
        return res

    def commit(self, f: Polynomial[FElt]) -> Commitment:
        a_vec: List[FElt] = f.coeffs

        d = nearest_larger_power_of_2(len(a_vec))
        for _ in range(d - len(a_vec)):
            a_vec.append(self.field_class.zero()) 
        
        randomness = self.crs.H * self.r.n
        return BulletproofsCommitment(
            value=self.__multiScalarMultiplication(scalars=a_vec, groupElts=self.crs.G_elts[:d]) + randomness
        )
    
    def open(self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any) -> Opening:
        if not isinstance(cm, BulletproofsCommitment):
            raise Exception('Must provide Bulletproofs commitment to Bulletproofs prover!')

        transcript = Transcript(field_class=self.field_class)
        transcript.append(cm)
        transcript.append(z)
        transcript.append(s)
        u_randomness = transcript.get_hash()
        U = self.crs.G_elts[0].generator() * u_randomness.n # TODO: Remove class reference from instance 
        P_prime = cm.value + (U * s.n)

        a_vec = f.coeffs
        d = nearest_larger_power_of_2(len(a_vec))
        k = get_power_of_2(d) # Yeah, could just use a log here
        for _ in range(d - len(a_vec)):
            a_vec.append(self.field_class.zero())
        g_vec = self.crs.G_elts[:d]
        b_vec = [self.field_class.one()]
        for _ in range(d - 1):
            b_vec.append(b_vec[-1] * z)

        L_js = []
        R_js = []
        Q = P_prime
        r_prime = self.r
        for _ in range(k):
            a_lo, a_hi = self.__split_lo_hi(a_vec)
            b_lo, b_hi = self.__split_lo_hi(b_vec)
            g_lo, g_hi = self.__split_lo_hi(g_vec)

            l_j = transcript.get_hash(salt=bytes(1))
            r_j = transcript.get_hash(salt=bytes(2))
            L_j = self.__multiScalarMultiplication(scalars=a_lo, groupElts=g_hi) + \
                self.crs.H * l_j.n + \
                U * self.__scalarDotProduct(a=a_lo, b=b_hi)
            R_j = self.__multiScalarMultiplication(scalars=a_hi, groupElts=g_lo) + \
                self.crs.H * r_j.n + \
                U * self.__scalarDotProduct(a=a_hi, b=b_lo)
            L_js.append(L_j)
            R_js.append(R_j)
            transcript.append(L_j)
            transcript.append(R_j)
            
            u_j = transcript.get_hash()
            u_j_inv = self.field_class.one() / u_j
            a_vec = self.__add_vec(self.__scale_vec(a_hi, u_j_inv), self.__scale_vec(a_lo, u_j))
            b_vec = self.__add_vec(self.__scale_vec(b_lo, u_j_inv), self.__scale_vec(b_hi, u_j))
            g_vec = self.__add_vec(self.__scale_vec(g_lo, u_j_inv), self.__scale_vec(g_hi, u_j))
            r_prime += l_j * u_j * u_j + r_j * u_j_inv * u_j_inv
            Q += L_j * (u_j * u_j) + R_j * (u_j_inv * u_j_inv)
        
        a = a_vec
        b = b_vec
        g = g_vec
        r_1 = transcript.get_hash(salt=bytes(1))
        r_2 = transcript.get_hash(salt=bytes(2))
        R = (g + (U * b)) * r_1 + self.crs.H * r_2
        transcript.append(R)

        c = transcript.get_hash()
        z_1 = a * c + r_1
        z_2 = r_prime * c + r_2

        return BulletproofsOpening(
            value=BulletproofsOpeningProof(
                L_js=L_js,
                R_js=R_js,
                R=R,
                z_1=z_1,
                z_2=z_2,
            )
        )

class BulletproofsVerifier(PCSVerifier, Generic[FElt, CyclicGroupElt]):
    def __init__(self, crs: BulletproofsCRS, field_class: Type[FElt]):
        self.crs: BulletproofsCRS = crs
        self.field_class: Type[FElt] = field_class

    def verify_opening(self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any) -> bool:
        if not isinstance(op, BulletproofsOpening):
            raise Exception('Must provide Bulletproofs opening to Bulletproofs verifier!')
        if not isinstance(cm, BulletproofsCommitment):
            raise Exception('Must provide Bulletproofs commitment to Bulletproofs verifier!')

        # ---------- Re-execute transcript based on proof values ----------
        transcript = Transcript(field_class=self.field_class)
        transcript.append(cm)
        transcript.append(z)
        transcript.append(s)
        u_randomness = transcript.get_hash()
        U = self.crs.G_elts[0].generator() * u_randomness.n # TODO: Remove class reference from instance 
        P_prime = cm.value + (U * s.n)
        L_js = op.value.L_js
        R_js = op.value.R_js
        u_js = []
        u_js_inv = []
        k = len(L_js)
        for i in range(k):
            transcript.append(L_js[i])
            transcript.append(R_js[i])
            u_j = transcript.get_hash()
            u_js.append(u_j)
            u_js_inv.append(self.field_class.one() / u_j)
        R = op.value.R
        transcript.append(R)

        # ---------- Compute derived G and b values ----------
        d = 2 ** k
        g_vec = self.crs.G_elts[:d]
        b_vec = [self.field_class.one()]
        for _ in range(d - 1):
            b_vec.append(b_vec[-1] * z)
        s_vec = []
        for i in range(d):
            ind = i
            prod = self.field_class.one()
            for j in range(k):
                if ind % 2 == 0:
                    prod *= u_js_inv[j]
                else:
                    prod *= u_js[j]
                ind //= 2
        g = g_vec * s_vec
        b = b_vec * s_vec

        # ---------- Verify Schnorr proof using randomness from transcript ----------
        c = transcript.get_hash()
        LHS = (P_prime * c) + R
        H = self.crs.H
        z_1 = op.value.z_1
        z_2 = op.value.z_2
        RHS = (g + (U * b)) * z_1 + H * z_2 

        return LHS == RHS