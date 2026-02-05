import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer

simulator = Aer.get_backend("qasm_simulator")

def eve_intercept(circuit, eve_basis):
    qc = circuit.copy()
    if eve_basis == "X":
        qc.h(0)
    qc.measure(0, 0)

    result = simulator.run(qc, shots=1).result()
    measured = int(list(result.get_counts().keys())[0])

    resend = QuantumCircuit(1, 1)
    if measured == 1:
        resend.x(0)
    if eve_basis == "X":
        resend.h(0)

    return resend

def apply_eve(circuit, eve_probability):
    if np.random.rand() < eve_probability:
        eve_basis = np.random.choice(["Z", "X"])
        return eve_intercept(circuit, eve_basis)
    return circuit
