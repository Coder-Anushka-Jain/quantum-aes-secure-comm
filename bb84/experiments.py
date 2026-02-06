"""
BB84 Experiment Wrappers

This module provides high-level functions to run BB84 experiments
with and without Eve's presence.
"""

import numpy as np
from typing import Dict
from .bb84_core import bb84_protocol
from .eve_attack import eve_intercept_resend


def run_bb84(num_qubits: int) -> Dict:
    """
    Run BB84 protocol without any eavesdropping.
    
    Args:
        num_qubits: Number of qubits to transmit
    
    Returns:
        Dictionary with BB84 results including QBER and keys
    """
    result = bb84_protocol(num_qubits)
    result['eve_present'] = False
    result['eve_probability'] = 0.0
    return result


def run_bb84_with_eve(num_qubits: int, eve_probability: float) -> Dict:
    """
    Run BB84 protocol with Eve performing intercept-resend attack.
    
    Args:
        num_qubits: Number of qubits to transmit
        eve_probability: Probability that Eve intercepts each qubit
    
    Returns:
        Dictionary with BB84 results including QBER and keys
    """
    # Step 1: Alice generates bits and bases
    alice_bits = np.random.randint(0, 2, num_qubits)
    alice_bases = np.random.randint(0, 2, num_qubits)
    
    # Step 2: Alice encodes qubits
    from .bb84_core import encode_qubits
    alice_qubits = encode_qubits(alice_bits, alice_bases)
    
    # Step 3: Eve intercepts (with probability eve_probability)
    modified_qubits, modified_bases, interceptions = eve_intercept_resend(
        alice_qubits, alice_bases, eve_probability
    )
    
    # Step 4: Bob selects bases and measures
    bob_bases = np.random.randint(0, 2, num_qubits)
    
    from .bb84_core import measure_qubits
    bob_bits = measure_qubits(modified_qubits, modified_bases, bob_bases)
    
    # Step 5: Basis reconciliation
    matching_bases = alice_bases == bob_bases
    alice_sifted_key = alice_bits[matching_bases]
    bob_sifted_key = bob_bits[matching_bases]
    
    # Step 6: Calculate QBER
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
        'total_qubits': num_qubits,
        'eve_present': True,
        'eve_probability': eve_probability,
        'eve_interceptions': interceptions
    }