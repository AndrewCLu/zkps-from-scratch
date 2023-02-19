from dataclasses import dataclass
from typing import List, Generic, Any
from algebra import FElt, Polynomial
from constraints import PlonkConstraints
from preprocessor import PlonkPreprocessedInput
from polynomial_commitment_schemes.pcs import PCSProver, PCSVerifier

@dataclass
class PlonkProof(Generic[FElt]):
    x: Any
    y: Any
    
class PlonkProver(Generic[FElt]):
    def __init__(self, pcs_prover: PCSProver[FElt], preprocessed_input: PlonkPreprocessedInput[FElt]) -> None:
        self.pcs_prover: PCSProver[FElt] = pcs_prover
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input

    def prove(self, witness: List[FElt]) -> PlonkProof[FElt]:
        f = Polynomial[FElt]([witness[0].one()] * 4)
        cm = self.pcs_prover.commit(f)
        return PlonkProof(cm, self.pcs_prover.open(f, cm, witness[0].one() * 2, witness[0].one() * 15, None))

class PlonkVerifier(Generic[FElt]):
    def __init__(self, pcs_verifier: PCSVerifier[FElt], preprocessed_input: PlonkPreprocessedInput[FElt]) -> None:
        self.pcs_verifier: PCSVerifier[FElt] = pcs_verifier
        self.preprocessed_input: PlonkPreprocessedInput[FElt] = preprocessed_input
    
    def verify(self, proof: PlonkProof[FElt], publicInputs: List[FElt]) -> bool:
        return self.pcs_verifier.verify_opening(proof.y, proof.x, publicInputs[0].one() * 2, publicInputs[0].one() * 15, None)