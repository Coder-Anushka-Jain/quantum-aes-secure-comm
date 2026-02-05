"""
LEGACY FILE — DO NOT USE FOR EXPERIMENTS OR DEPLOYMENT

This script contains an early monolithic implementation of the BB84
Quantum Key Distribution protocol with AES integration.

It is retained for:
- Reference
- Reproducibility
- Version history

Active development uses modular files in the `bb84/` directory:
- bb84_core.py
- eve_attack.py
- experiments.py
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer
import matplotlib.pyplot as plt

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_QUBITS = 1024
QBER_THRESHOLD = 0.11
simulator = Aer.get_backend('qasm_simulator')

# -----------------------------
# ALICE GENERATES BITS & BASES
# -----------------------------
alice_bits = np.random.randint(2, size=NUM_QUBITS)
alice_bases = np.random.choice(['Z', 'X'], size=NUM_QUBITS)

print("Alice bits:  ", alice_bits)
print("Alice bases: ", alice_bases)

# -----------------------------
# QUBIT ENCODING FUNCTION
# -----------------------------
def encode_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)

    if bit == 1:
        qc.x(0)

    if basis == 'X':
        qc.h(0)

    return qc

# -----------------------------
# EVE INTERCEPT–RESEND ATTACK
# -----------------------------
def eve_intercept(circuit, eve_basis): 
    eve_circuit = circuit.copy()

    if eve_basis == 'X':
        eve_circuit.h(0)

    eve_circuit.measure(0, 0)

    job = simulator.run(eve_circuit, shots=1)
    result = job.result()
    measured_bit = int(list(result.get_counts().keys())[0])

    resend = QuantumCircuit(1, 1)

    if measured_bit == 1:
        resend.x(0)

    if eve_basis == 'X':
        resend.h(0)

    return resend

# -----------------------------
# ALICE PREPARES QUBITS
# -----------------------------
alice_circuits = [
    encode_qubit(alice_bits[i], alice_bases[i])
    for i in range(NUM_QUBITS)
]

# -----------------------------
# BOB & EVE BASE SELECTION
# -----------------------------
bob_bases = np.random.choice(['Z', 'X'], size=NUM_QUBITS)
eve_bases = np.random.choice(['Z', 'X'], size=NUM_QUBITS)
bob_results = []

# -----------------------------
# TRANSMISSION: ALICE → EVE → BOB
# -----------------------------
for i in range(NUM_QUBITS):
    qc = alice_circuits[i]

    # Eve intercepts
    qc = eve_intercept(qc, eve_bases[i])

    # Bob measures
    if bob_bases[i] == 'X':
        qc.h(0)

    qc.measure(0, 0)

    job = simulator.run(qc, shots=1)
    result = job.result()
    measured_bit = int(list(result.get_counts().keys())[0])

    bob_results.append(measured_bit)

print("Bob bases:   ", bob_bases)
print("Bob results: ", bob_results)

# -----------------------------
# BASIS RECONCILIATION
# -----------------------------
alice_key = []
bob_key = []

for i in range(NUM_QUBITS):
    if alice_bases[i] == bob_bases[i]:
        alice_key.append(alice_bits[i])
        bob_key.append(bob_results[i])

print("Alice final key:", alice_key)
print("Bob final key:  ", bob_key)

# -----------------------------
# QBER CALCULATION
# -----------------------------
errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
qber = errors / len(alice_key) if len(alice_key) > 0 else 0

print("Errors:", errors)
print("QBER:", qber)

# -----------------------------
# QBER GRAPH
# -----------------------------
plt.bar(["QBER"], [qber])
plt.axhline(y=QBER_THRESHOLD, color='r', linestyle='--',
            label="Security Threshold (11%)")
plt.ylabel("Error Rate")
plt.title("QBER under Intercept–Resend Attack")
plt.legend()
plt.show()

# -----------------------------
# QUANTUM KEY → AES KEY
# -----------------------------
def quantum_key_to_aes_key(bit_list):
    bit_string = ''.join(map(str, bit_list))
    key_bits = (bit_string * 128)[:128]
    return int(key_bits, 2).to_bytes(16, byteorder='big')

# -----------------------------
# AES ENCRYPT / DECRYPT
# -----------------------------
def aes_encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv, ciphertext

def aes_decrypt(iv, ciphertext, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

# -----------------------------
# SECURE COMMUNICATION DECISION
# -----------------------------
if qber <= QBER_THRESHOLD:
    print("\nChannel secure. Proceeding with AES encryption.")

    aes_key = quantum_key_to_aes_key(alice_key)

    message = "Quantum cryptography secures the future!"
    iv, ciphertext = aes_encrypt(message, aes_key)
    decrypted_message = aes_decrypt(iv, ciphertext, aes_key)

    print("Original message: ", message)
    print("Encrypted message:", ciphertext)
    print("Decrypted message:", decrypted_message)

else:
    print("\nChannel NOT secure. Key discarded due to high QBER.")


