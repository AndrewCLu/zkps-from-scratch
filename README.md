# PLONK from scratch

This is an implementation of the PLONK zero knowledge proof system with two goals in mind:

1. Understandability
2. Composability

We aim to construct PLONK through modular, well-interfaced building blocks. Polynomial commitment schemas are detached from PIOPs, algebraic objects are self-contained classes, and the prover and verifier themselves make no assumption about the commitment scheme or choice of field. Simultaneously, we hope that this implementation is easy to understand. Ideally, it could serve as a model for one's first implementation of a zero knowledge proof system. Our abstractions make it clear what assumptions and requirements are being made by the proof system at every step along the way. For example, one can run this version of PLONK with a trivial polynomial commitment scheme, one where the prover commits to a polynomial by just sending over its coefficients. This is clearly not a hiding scheme, but it shows how decoupled the commitment scheme can be from the rest of the proof system.

Another goal for this implementation is for ease of rough metrics and benchmarking. We want it to be easy to swap out one commitment scheme, elliptic curve, or field for another, and see how the system performs on a certain instance. This code will not be optimized, but it can give one a good sense of how many operations of a given type the final system will produce.

In the future, we plan on expanding this repository to implementations of various proof systems. The challenge will be to see how we can retain modularity, especially when it comes to recursive proof systems that "break into" the inner details of a proof system.
