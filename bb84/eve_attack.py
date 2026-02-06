"""
Eve's Intercept-Resend Attack Implementation

This module simulates an eavesdropper (Eve) performing an intercept-resend
attack on the BB84 protocol. Eve intercepts qubits, measures them in a
randomly chosen basis, and resends new qubits to Bob.
"""

import numpy as np
from typing import Tuple


def eve_intercept_resend(alice_qubits: np.ndarray, alice_bases: np.ndarray,
                         eve_probability: float) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Simulate Eve's intercept-resend attack on the quantum channel.
    
    Eve intercepts qubits with probability eve_probability. For each intercepted
    qubit, Eve:
    1. Randomly selects a measurement basis
    2. Measures the qubit (collapsing its state)
    3. Prepares a new qubit in the measured state
    4. Sends it to Bob
    
    This introduces errors when Eve's basis doesn't match Alice's basis.
    
    Args:
        alice_qubits: Original qubits from Alice (bit, basis pairs)
        alice_bases: Alice's encoding bases
        eve_probability: Probability that Eve intercepts each qubit
    
    Returns:
        Tuple of:
            - modified_qubits: Qubits after potential Eve interception
            - modified_bases: Bases after potential Eve interception
            - interceptions: Number of qubits intercepted by Eve
    """
    num_qubits = len(alice_qubits)
    alice_bits = alice_qubits[:, 0].astype(int)
    
    # Create copies that may be modified by Eve
    modified_bits = alice_bits.copy()
    modified_bases = alice_bases.copy()
    
    # Track number of interceptions
    interceptions = 0
    
    for i in range(num_qubits):
        # Eve intercepts with probability eve_probability
        if np.random.random() < eve_probability:
            interceptions += 1
            
            # Eve randomly selects a measurement basis
            eve_basis = np.random.randint(0, 2)
            
            # Eve measures the qubit
            if eve_basis == alice_bases[i]:
                # Eve's basis matches Alice's: measurement is deterministic
                eve_bit = alice_bits[i]
            else:
                # Eve's basis differs: measurement is random (50/50)
                eve_bit = np.random.randint(0, 2)
            
            # Eve prepares and sends a new qubit in the measured state
            # This effectively changes the qubit that Bob will receive
            modified_bits[i] = eve_bit
            modified_bases[i] = eve_basis
    
    # Reconstruct modified qubits
    modified_qubits = np.column_stack((modified_bits, modified_bases))
    
    return modified_qubits, modified_bases, interceptions