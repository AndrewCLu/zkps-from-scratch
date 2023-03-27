from typing import Generic, List, Type, Any
from dataclasses import dataclass
from algebra.field import FElt
from algebra.cyclic_group import CyclicGroupElt
from algebra.polynomial import Polynomial
from algebra.algorithms import (
    multi_scalar_multiplication,
    scalar_dot_product,
    split_vec,
    add_vec,
    scale_vec,
)
from polynomial_commitment_schemes.pcs import (
    Commitment,
    Opening,
    PCSProver,
    PCSVerifier,
)
from utils import nearest_larger_power_of_2, get_power_of_2
from transcript import Transcript


@dataclass
class BulletproofsCRS(Generic[FElt, CyclicGroupElt]):
    G_elts: List[CyclicGroupElt]
    H: CyclicGroupElt

    @staticmethod
    # This is not secure since we are generating deterministically
    def common_setup(
        d: int, cyclic_group_class: Type[CyclicGroupElt]
    ) -> "BulletproofsCRS":
        G_elts = []
        g = cyclic_group_class.generator()
        for i in range(d):
            G_elts.append(g * i)
        H = g * d

        return BulletproofsCRS(G_elts=G_elts, H=H)


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


@dataclass
class BulletproofsBatchOpening(Opening):
    value: List[BulletproofsOpeningProof]


class BulletproofsProver(PCSProver, Generic[FElt, CyclicGroupElt]):
    def __init__(
        self,
        crs: BulletproofsCRS,
        field_class: Type[FElt],
        cyclic_group_class: Type[CyclicGroupElt],
    ):
        self.crs: BulletproofsCRS = crs
        self.field_class: Type[FElt] = field_class
        self.cyclic_group_class: Type[CyclicGroupElt] = cyclic_group_class
        self.r: FElt = self.field_class(1234)  # Fix randomness for consistent testing

    def commit(self, f: Polynomial[FElt]) -> Commitment:
        a_vec: List[FElt] = f.coeffs

        d = nearest_larger_power_of_2(len(a_vec))
        for _ in range(d - len(a_vec)):
            a_vec.append(self.field_class.zero())

        randomness = self.crs.H * self.r
        return BulletproofsCommitment(
            value=multi_scalar_multiplication(
                scalars=a_vec, groupElts=self.crs.G_elts[:d]
            )
            + randomness
        )

    def open(
        self, f: Polynomial[FElt], cm: Commitment, z: FElt, s: FElt, op_info: Any
    ) -> Opening:
        if not isinstance(cm, BulletproofsCommitment):
            raise ValueError(
                "Must provide Bulletproofs commitment to Bulletproofs prover!"
            )

        transcript = Transcript(field_class=self.field_class)
        transcript.append(cm)
        transcript.append(z)
        transcript.append(s)
        u_randomness = transcript.get_hash()
        U = self.cyclic_group_class.generator() * u_randomness

        # ---------- Compute initial values of a_vec, b_vec, g_vec ----------

        a_vec = f.coeffs
        d = nearest_larger_power_of_2(len(a_vec))
        k = get_power_of_2(d)  # Yeah, could just use a log here
        for _ in range(d - len(a_vec)):
            a_vec.append(self.field_class.zero())
        g_vec = self.crs.G_elts[:d]
        b_vec = [self.field_class.one()]
        for _ in range(d - 1):
            b_vec.append(b_vec[-1] * z)

        # ---------- Run algorithm to transform vectors down to points ----------

        L_js = []
        R_js = []
        r_prime = self.r
        for _ in range(k):
            a_lo, a_hi = split_vec(a_vec)
            b_lo, b_hi = split_vec(b_vec)
            g_lo, g_hi = split_vec(g_vec)

            l_j = transcript.get_hash(salt=bytes(1))
            r_j = transcript.get_hash(salt=bytes(2))
            L_j = (
                multi_scalar_multiplication(scalars=a_lo, groupElts=g_hi)
                + self.crs.H * l_j
                + U * scalar_dot_product(aa=a_lo, bb=b_hi)
            )
            R_j = (
                multi_scalar_multiplication(scalars=a_hi, groupElts=g_lo)
                + self.crs.H * r_j
                + U * scalar_dot_product(aa=a_hi, bb=b_lo)
            )
            L_js.append(L_j)
            R_js.append(R_j)
            transcript.append(L_j)
            transcript.append(R_j)

            u_j = transcript.get_hash()
            u_j_inv = self.field_class.one() / u_j
            a_vec = add_vec(scale_vec(a_hi, u_j_inv), scale_vec(a_lo, u_j))
            b_vec = add_vec(scale_vec(b_lo, u_j_inv), scale_vec(b_hi, u_j))
            g_vec = add_vec(scale_vec(g_lo, u_j_inv), scale_vec(g_hi, u_j))
            r_prime += l_j * u_j * u_j + r_j * u_j_inv * u_j_inv

        # ---------- Run Schnorr protocol ----------

        if len(a_vec) != 1 or len(b_vec) != 1 or len(g_vec) != 1:
            raise AssertionError("Failed to compute final values of a, b, g!")
        a = a_vec[0]
        b = b_vec[0]
        g = g_vec[0]
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

    def batch_open_at_point(
        self,
        fs: List[Polynomial[FElt]],
        cms: List[Commitment],
        z: FElt,
        ss: List[FElt],
        op_info: Any,
    ) -> Opening:
        batch_size = len(fs)
        if len(cms) != batch_size or len(ss) != batch_size:
            raise ValueError("All parameters must have length equal to batch size!")

        batch_ops = []
        for i in range(batch_size):
            if not isinstance(cms[i], BulletproofsCommitment):
                raise ValueError(
                    "Wrong commitment used. Must provide a Bulletproofs commitment."
                )

            op = self.open(f=fs[i], cm=cms[i], z=z, s=ss[i], op_info=op_info)
            batch_ops.append(op.value)

        return BulletproofsBatchOpening(value=batch_ops)


class BulletproofsVerifier(PCSVerifier, Generic[FElt, CyclicGroupElt]):
    def __init__(
        self,
        crs: BulletproofsCRS,
        field_class: Type[FElt],
        cyclic_group_class: Type[CyclicGroupElt],
    ):
        self.crs: BulletproofsCRS = crs
        self.field_class: Type[FElt] = field_class
        self.cyclic_group_class: Type[CyclicGroupElt] = cyclic_group_class

    def verify_opening(
        self, op: Opening, cm: Commitment, z: FElt, s: FElt, op_info: Any
    ) -> bool:
        if not isinstance(op, BulletproofsOpening):
            raise ValueError(
                "Must provide Bulletproofs opening to Bulletproofs verifier!"
            )
        if not isinstance(cm, BulletproofsCommitment):
            raise ValueError(
                "Must provide Bulletproofs commitment to Bulletproofs verifier!"
            )

        # ---------- Re-execute transcript based on proof values ----------

        transcript = Transcript(field_class=self.field_class)
        transcript.append(cm)
        transcript.append(z)
        transcript.append(s)
        u_randomness = transcript.get_hash()
        U = self.cyclic_group_class.generator() * u_randomness
        P_prime = cm.value + (U * s)

        L_js = op.value.L_js
        R_js = op.value.R_js
        k = len(L_js)
        u_js: List[FElt] = []
        u_js_inv: List[FElt] = []
        Q = P_prime
        for i in range(k):
            transcript.append(L_js[i])
            transcript.append(R_js[i])
            u_j = transcript.get_hash()
            u_j_inv = self.field_class.one() / u_j
            # u_js are computed in reverse order
            u_js.insert(0, u_j)
            u_js_inv.insert(0, u_j_inv)
            Q += L_js[i] * (u_j * u_j) + R_js[i] * (u_j_inv * u_j_inv)
        R = op.value.R
        transcript.append(R)

        # ---------- Compute derived G and b values ----------

        d = 2**k
        g_vec = self.crs.G_elts[:d]
        b_vec = [self.field_class.one()]
        for _ in range(d - 1):
            b_vec.append(b_vec[-1] * z)
        s_vec: List[FElt] = []
        for i in range(d):
            ind = i
            prod = self.field_class.one()
            for j in range(k):
                if ind % 2 == 0:
                    prod *= u_js_inv[j]
                else:
                    prod *= u_js[j]
                ind //= 2
            s_vec.append(prod)
        g = multi_scalar_multiplication(scalars=s_vec, groupElts=g_vec)
        b = scalar_dot_product(aa=s_vec, bb=b_vec)

        # ---------- Verify Schnorr proof using randomness from transcript ----------

        c = transcript.get_hash()
        LHS = (Q * c) + R
        H = self.crs.H
        z_1 = op.value.z_1
        z_2 = op.value.z_2
        RHS = (g + (U * b)) * z_1 + H * z_2

        return LHS == RHS

    def verify_batch_at_point(
        self, op: Opening, cms: List[Commitment], z: FElt, ss: List[FElt], op_info: Any
    ) -> bool:
        if not isinstance(op, BulletproofsBatchOpening):
            raise ValueError(
                "Wrong opening used. Must provide a Bulletproofs Batch opening."
            )

        batch_size = len(cms)
        if len(ss) != batch_size:
            raise ValueError("All parameters must have length equal to batch size!")

        for i in range(batch_size):
            if not isinstance(cms[i], BulletproofsCommitment):
                raise ValueError(
                    "Wrong commitment used. Must provide a Bulletproofs commitment."
                )

            op_i = BulletproofsOpening(value=op.value[i])
            valid_op = self.verify_opening(
                op=op_i, cm=cms[i], z=z, s=ss[i], op_info=op_info
            )
            if not valid_op:
                return False

        return True
