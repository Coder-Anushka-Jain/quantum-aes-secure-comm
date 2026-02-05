import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer

simulator = Aer.get_backend("qasm_simulator")

def encode_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == "X":
        qc.h(0)
    return qc

def run_bb84(num_qubits=1024):
    alice_bits = np.random.randint(2, size=num_qubits)
    alice_bases = np.random.choice(["Z", "X"], size=num_qubits)
    bob_bases = np.random.choice(["Z", "X"], size=num_qubits)

    bob_results = []

    for i in range(num_qubits):
        qc = encode_qubit(alice_bits[i], alice_bases[i])
        if bob_bases[i] == "X":
            qc.h(0)
        qc.measure(0, 0)

        result = simulator.run(qc, shots=1).result()
        measured = int(list(result.get_counts().keys())[0])
        bob_results.append(measured)

    alice_key, bob_key = [], []

    for i in range(num_qubits):
        if alice_bases[i] == bob_bases[i]:
            alice_key.append(alice_bits[i])
            bob_key.append(bob_results[i])

    return alice_key, bob_key
