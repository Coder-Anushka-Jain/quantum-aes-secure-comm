"""
Experiment Runner for BB84 Protocol

This module provides functions to run single experiments and parameter sweeps
for analyzing BB84 performance under various conditions.
"""

import numpy as np
from typing import Dict, List
from .experiments import run_bb84, run_bb84_with_eve


def run_experiment(num_qubits: int, eve_enabled: bool, eve_probability: float = 0.0) -> Dict:
    """
    Run a single BB84 experiment with configurable parameters.
    
    Args:
        num_qubits: Number of qubits to transmit
        eve_enabled: Whether to enable Eve's intercept-resend attack
        eve_probability: Probability of Eve intercepting each qubit (if enabled)
    
    Returns:
        Dictionary containing experiment results
    """
    if eve_enabled:
        return run_bb84_with_eve(num_qubits, eve_probability)
    else:
        return run_bb84(num_qubits)


def run_eve_sweep(num_qubits: int, eve_probs: List[float], trials: int = 10) -> List[Dict]:
    """
    Run multiple BB84 experiments sweeping Eve's interception probability.
    
    This is useful for analyzing how QBER scales with Eve's presence.
    
    Args:
        num_qubits: Number of qubits per experiment
        eve_probs: List of Eve interception probabilities to test
        trials: Number of trials per probability value
    
    Returns:
        List of dictionaries, each containing:
            - eve_probability: The Eve probability tested
            - mean_qber: Average QBER across trials
            - std_qber: Standard deviation of QBER
            - mean_key_length: Average final key length
            - std_key_length: Standard deviation of key length
    """
    results = []
    
    for eve_prob in eve_probs:
        qbers = []
        key_lengths = []
        
        for _ in range(trials):
            result = run_bb84_with_eve(num_qubits, eve_prob)
            qbers.append(result['qber'])
            key_lengths.append(len(result['alice_key']))
        
        results.append({
            'eve_probability': eve_prob,
            'mean_qber': np.mean(qbers),
            'std_qber': np.std(qbers),
            'mean_key_length': np.mean(key_lengths),
            'std_key_length': np.std(key_lengths)
        })
    
    return results