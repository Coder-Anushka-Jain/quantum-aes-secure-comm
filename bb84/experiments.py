import numpy as np
from bb84.bb84_core import encode_qubit
from bb84.eve_attack import apply_eve
from qiskit_aer import Aer

simulator = Aer.get_backend("qasm_simulator")

def run_bb84_with_eve(num_qubits=1024, eve_probability=0.0):
    alice_bits = np.random.randint(2, size=num_qubits)
    alice_bases = np.random.choice(["Z", "X"], size=num_qubits)
    bob_bases = np.random.choice(["Z", "X"], size=num_qubits)

    bob_results = []

    for i in range(num_qubits):
        qc = encode_qubit(alice_bits[i], alice_bases[i])
        qc = apply_eve(qc, eve_probability)

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

    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    qber = errors / len(alice_key) if len(alice_key) else 0

    return {
        "alice_key": alice_key,
        "bob_key": bob_key,
        "qber": qber,
        "secure": qber < 0.11
    }
