"""
Secret Key Rate Calculator for Decoy-State BB84

Implements the simplified decoy-state key rate formula:
R = Q1 * (1 - H(e1)) - Qμ * f * H(Eμ)

Based on standard decoy-state QKD analysis.
"""

import numpy as np
from typing import Dict, Optional


def binary_entropy(x: float) -> float:
    """
    Compute binary entropy H(x) = -x*log2(x) - (1-x)*log2(1-x)
    
    Args:
        x: Probability value in [0, 1]
    
    Returns:
        Binary entropy value
    
    Note:
        Returns 0 for x=0 or x=1 (limit cases)
    """
    if x <= 0 or x >= 1:
        return 0.0
    
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


def compute_secret_key_rate(
    qber: float,
    detections: int,
    sent_pulses: int,
    mu: float = 0.5,
    f: float = 1.16,
    include_details: bool = False
) -> float:
    """
    Compute secret key rate for decoy-state BB84.
    
    Uses simplified formula:
    R = Q1 * (1 - H(e1)) - Qμ * f * H(Eμ)
    
    Where:
    - Q1 = single-photon gain ≈ Qμ * exp(-μ)
    - e1 = single-photon error rate ≈ QBER
    - Qμ = overall gain = detections / sent_pulses
    - Eμ = overall QBER
    - f = error correction efficiency (typically 1.16)
    - μ = mean photon number for signal pulses
    
    Args:
        qber: Quantum bit error rate (Eμ)
        detections: Number of detected pulses
        sent_pulses: Total number of sent pulses
        mu: Mean photon number for signal state (default: 0.5)
        f: Error correction efficiency (default: 1.16)
        include_details: If True, return detailed breakdown
    
    Returns:
        Secret key rate R (bits per pulse)
        If include_details=True, returns dict with breakdown
    """
    # Compute overall gain Qμ
    if sent_pulses == 0:
        Q_mu = 0.0
    else:
        Q_mu = detections / sent_pulses
    
    # Compute single-photon gain Q1
    Q1 = Q_mu * np.exp(-mu)
    
    # Single-photon error rate (simplified: assume e1 ≈ QBER)
    e1 = qber
    
    # Overall QBER
    E_mu = qber
    
    # Compute binary entropies
    H_e1 = binary_entropy(e1)
    H_Emu = binary_entropy(E_mu)
    
    # Secret key rate formula
    R = Q1 * (1 - H_e1) - Q_mu * f * H_Emu
    
    # Key rate cannot be negative
    R = max(0.0, R)
    
    if include_details:
        return {
            'key_rate': R,
            'Q_mu': Q_mu,
            'Q1': Q1,
            'e1': e1,
            'E_mu': E_mu,
            'H_e1': H_e1,
            'H_Emu': H_Emu,
            'mu': mu,
            'f': f
        }
    
    return R


def compute_key_rate_from_result(
    result: Dict,
    mu: float = 0.5,
    f: float = 1.16
) -> float:
    """
    Compute key rate from BB84 experiment result dictionary.
    
    Args:
        result: Dictionary from run_experiment or run_adaptive_experiment
        mu: Mean photon number
        f: Error correction efficiency
    
    Returns:
        Secret key rate (bits per pulse)
    """
    qber = result.get('qber', 0.0)
    
    # Detections = matching bases (sifted key length)
    detections = result.get('matching_bases_count', 0)
    
    # Total sent pulses
    sent_pulses = result.get('total_qubits', 1)
    
    return compute_secret_key_rate(
        qber=qber,
        detections=detections,
        sent_pulses=sent_pulses,
        mu=mu,
        f=f
    )


def analyze_key_rate_statistics(key_rates: list) -> Dict:
    """
    Compute statistics for a list of key rates.
    
    Args:
        key_rates: List of key rate values
    
    Returns:
        Dictionary with mean, std, min, max
    """
    if not key_rates:
        return {
            'mean': 0.0,
            'std': 0.0,
            'min': 0.0,
            'max': 0.0,
            'positive_rate_fraction': 0.0
        }
    
    key_rates_array = np.array(key_rates)
    
    return {
        'mean': np.mean(key_rates_array),
        'std': np.std(key_rates_array),
        'min': np.min(key_rates_array),
        'max': np.max(key_rates_array),
        'positive_rate_fraction': np.sum(key_rates_array > 0) / len(key_rates_array)
    }


def compute_theoretical_key_rate(
    eve_probability: float,
    mu: float = 0.5,
    f: float = 1.16,
    eta: float = 0.5
) -> float:
    """
    Compute theoretical key rate for given Eve probability.
    
    Assumes:
    - QBER ≈ 0.25 * eve_probability (intercept-resend)
    - Detection efficiency η (eta)
    - Basis matching probability ≈ 0.5
    
    Args:
        eve_probability: Eve's interception probability
        mu: Mean photon number
        f: Error correction efficiency
        eta: Detection efficiency (default: 0.5 for basis matching)
    
    Returns:
        Theoretical secret key rate
    """
    # Theoretical QBER from intercept-resend
    qber = 0.25 * eve_probability
    
    # Overall gain (simplified)
    Q_mu = eta * (1 - np.exp(-mu))
    
    # Single-photon gain
    Q1 = Q_mu * np.exp(-mu)
    
    # Entropies
    e1 = qber
    H_e1 = binary_entropy(e1)
    H_Emu = binary_entropy(qber)
    
    # Key rate
    R = Q1 * (1 - H_e1) - Q_mu * f * H_Emu
    
    return max(0.0, R)