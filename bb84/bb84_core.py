"""
BB84 Quantum Key Distribution Protocol - Core Implementation

This module implements the BB84 protocol without any eavesdropping.
It handles Alice's bit and basis generation, Bob's basis selection,
basis reconciliation, and final key extraction.
"""

import numpy as np
from typing import Dict, List, Tuple


def bb84_protocol(num_qubits: int, alice_bits: np.ndarray = None, 
                  alice_bases: np.ndarray = None, bob_bases: np.ndarray = None) -> Dict:
    """
    Execute the BB84 quantum key distribution protocol.
    
    Args:
        num_qubits: Number of qubits to transmit
        alice_bits: Optional pre-generated Alice bits (for reproducibility)
        alice_bases: Optional pre-generated Alice bases (for reproducibility)
        bob_bases: Optional pre-generated Bob bases (for reproducibility)
    
    Returns:
        Dictionary containing:
            - qber: Quantum Bit Error Rate
            - alice_key: Final key bits from Alice's side
            - bob_key: Final key bits from Bob's side
            - matching_bases_count: Number of matching bases
            - total_qubits: Total qubits transmitted
    """
    
    # Step 1: Alice generates random bits
    if alice_bits is None:
        alice_bits = np.random.randint(0, 2, num_qubits)
    
    # Step 2: Alice selects random bases (0 = Z-basis, 1 = X-basis)
    if alice_bases is None:
        alice_bases = np.random.randint(0, 2, num_qubits)
    
    # Step 3: Alice encodes qubits based on bits and bases
    # In real QKD, this would be done with photon polarization
    # Here we simulate the classical information
    alice_qubits = encode_qubits(alice_bits, alice_bases)
    
    # Step 4: Bob selects random bases for measurement
    if bob_bases is None:
        bob_bases = np.random.randint(0, 2, num_qubits)
    
    # Step 5: Bob measures qubits in his chosen bases
    bob_bits = measure_qubits(alice_qubits, alice_bases, bob_bases)
    
    # Step 6: Basis reconciliation (public channel)
    # Alice and Bob compare bases and keep only matching ones
    matching_bases = alice_bases == bob_bases
    
    # Step 7: Extract sifted key (bits where bases matched)
    alice_sifted_key = alice_bits[matching_bases]
    bob_sifted_key = bob_bits[matching_bases]
    
    # Step 8: Calculate QBER (should be ~0% without Eve)
    if len(alice_sifted_key) > 0:
        errors = np.sum(alice_sifted_key != bob_sifted_key)
        qber = errors / len(alice_sifted_key)
    else:
        qber = 0.0
    
    return {
        'qber': qber,
        'alice_key': alice_sifted_key.tolist(),
        'bob_key': bob_sifted_key.tolist(),
        'matching_bases_count': np.sum(matching_bases),
        'total_qubits': num_qubits
    }


def encode_qubits(bits: np.ndarray, bases: np.ndarray) -> np.ndarray:
    """
    Encode classical bits into quantum states based on chosen bases.
    
    Z-basis (0): |0⟩ or |1⟩
    X-basis (1): |+⟩ or |-⟩
    
    Args:
        bits: Classical bits to encode
        bases: Bases to use for encoding
    
    Returns:
        Encoded quantum states (represented classically)
    """
    # In simulation, we just store the (bit, basis) pair
    # Real implementation would prepare photon polarization states
    qubits = np.column_stack((bits, bases))
    return qubits


def measure_qubits(qubits: np.ndarray, alice_bases: np.ndarray, 
                   bob_bases: np.ndarray) -> np.ndarray:
    """
    Simulate Bob measuring qubits in his chosen bases.
    
    If Bob's basis matches Alice's basis: measurement is deterministic
    If Bob's basis differs: measurement result is random (50/50)
    
    Args:
        qubits: Encoded quantum states from Alice
        alice_bases: Alice's encoding bases
        bob_bases: Bob's measurement bases
    
    Returns:
        Bob's measurement results
    """
    alice_bits = qubits[:, 0].astype(int)
    bob_bits = np.zeros(len(qubits), dtype=int)
    
    for i in range(len(qubits)):
        if alice_bases[i] == bob_bases[i]:
            # Matching bases: Bob gets Alice's bit with certainty
            bob_bits[i] = alice_bits[i]
        else:
            # Non-matching bases: Bob gets random result (50/50)
            bob_bits[i] = np.random.randint(0, 2)
    
    return bob_bits