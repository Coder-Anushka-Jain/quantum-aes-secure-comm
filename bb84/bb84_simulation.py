import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer



NUM_QUBITS = 32
alice_bits = np.random.randint(2, size=NUM_QUBITS)
alice_bases = np.random.choice(['Z', 'X'], size=NUM_QUBITS)

print("Alice bits:  ", alice_bits)
print("Alice bases: ", alice_bases)


def encode_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)

    # Encode bit
    if bit == 1:
        qc.x(0)

    # Change basis if needed
    if basis == 'X':
        qc.h(0)

    return qc


alice_circuits = []

for i in range(NUM_QUBITS):
    qc = encode_qubit(alice_bits[i], alice_bases[i])
    alice_circuits.append(qc)


bob_bases = np.random.choice(['Z', 'X'], size=NUM_QUBITS)
bob_results = []


simulator = Aer.get_backend('qasm_simulator')

for i in range(NUM_QUBITS):
    qc = alice_circuits[i]

    if bob_bases[i] == 'X':
        qc.h(0)

    qc.measure(0, 0)

    job = simulator.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    measured_bit = int(list(counts.keys())[0])

    bob_results.append(measured_bit)



print("Bob bases:   ", bob_bases)
print("Bob results: ", bob_results)


alice_key = []
bob_key = []

for i in range(NUM_QUBITS):
    if alice_bases[i] == bob_bases[i]:
        alice_key.append(alice_bits[i])
        bob_key.append(bob_results[i])

print("Alice final key:", alice_key)
print("Bob final key:  ", bob_key)


final_key = ''.join(map(str, alice_key))
print("Final Shared Secret Key:", final_key)
