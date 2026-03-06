"""
PNS Attack Experiments and Analysis

This module provides high-level functions to run PNS attack experiments
and compare with other attack strategies.
"""

import numpy as np
from typing import Dict, List
from .pns_attack import run_bb84_with_pns_attack
from .key_rate_calculator import compute_secret_key_rate


def run_pns_parameter_sweep(
    num_pulses: int = 1000,
    mu_signal_values: List[float] = None,
    trials: int = 10
) -> List[Dict]:
    """
    Sweep over different signal photon numbers to analyze PNS attack.
    
    Args:
        num_pulses: Pulses per experiment
        mu_signal_values: List of mean photon numbers to test
        trials: Trials per parameter value
    
    Returns:
        List of results for each parameter combination
    """
    if mu_signal_values is None:
        mu_signal_values = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    
    results = []
    
    for mu_signal in mu_signal_values:
        trial_qbers = []
        trial_key_lengths = []
        trial_detection_rates_signal = []
        trial_detection_rates_decoy = []
        trial_eve_info_gains = []
        trial_key_rates = []
        
        for _ in range(trials):
            result = run_bb84_with_pns_attack(
                num_pulses=num_pulses,
                mu_signal=mu_signal,
                mu_decoy=0.1
            )
            
            trial_qbers.append(result['qber'])
            trial_key_lengths.append(result['key_length'])
            trial_detection_rates_signal.append(
                result['detection_stats']['signal_detection_rate']
            )
            trial_detection_rates_decoy.append(
                result['detection_stats']['decoy_detection_rate']
            )
            trial_eve_info_gains.append(
                result['eve_results']['information_gain']
            )
            
            # Compute key rate
            key_rate = compute_secret_key_rate(
                qber=result['qber'],
                detections=result['key_length'],
                sent_pulses=num_pulses,
                mu=mu_signal
            )
            trial_key_rates.append(key_rate)
        
        results.append({
            'mu_signal': mu_signal,
            'mean_qber': np.mean(trial_qbers),
            'std_qber': np.std(trial_qbers),
            'mean_key_length': np.mean(trial_key_lengths),
            'std_key_length': np.std(trial_key_lengths),
            'mean_signal_detection_rate': np.mean(trial_detection_rates_signal),
            'std_signal_detection_rate': np.std(trial_detection_rates_signal),
            'mean_decoy_detection_rate': np.mean(trial_detection_rates_decoy),
            'std_decoy_detection_rate': np.std(trial_detection_rates_decoy),
            'mean_eve_info_gain': np.mean(trial_eve_info_gains),
            'std_eve_info_gain': np.std(trial_eve_info_gains),
            'mean_key_rate': np.mean(trial_key_rates),
            'std_key_rate': np.std(trial_key_rates)
        })
    
    return results


def compare_intercept_resend_vs_pns(
    num_pulses: int = 1000,
    eve_probability: float = 0.5,
    mu_signal: float = 0.5,
    trials: int = 10
) -> Dict:
    """
    Compare intercept-resend attack vs PNS attack.
    
    Args:
        num_pulses: Number of pulses
        eve_probability: Eve's interception probability (for IR attack)
        mu_signal: Mean photon number
        trials: Number of trials
    
    Returns:
        Comparison results
    """
    from .experiments import run_bb84_with_eve
    
    # PNS attack results
    pns_qbers = []
    pns_key_lengths = []
    pns_eve_info = []
    pns_key_rates = []
    
    for _ in range(trials):
        result = run_bb84_with_pns_attack(
            num_pulses=num_pulses,
            mu_signal=mu_signal
        )
        pns_qbers.append(result['qber'])
        pns_key_lengths.append(result['key_length'])
        pns_eve_info.append(result['eve_results']['information_gain'])
        
        key_rate = compute_secret_key_rate(
            qber=result['qber'],
            detections=result['key_length'],
            sent_pulses=num_pulses,
            mu=mu_signal
        )
        pns_key_rates.append(key_rate)
    
    # Intercept-Resend attack results
    ir_qbers = []
    ir_key_lengths = []
    ir_key_rates = []
    
    for _ in range(trials):
        result = run_bb84_with_eve(num_pulses, eve_probability)
        ir_qbers.append(result['qber'])
        ir_key_lengths.append(len(result['alice_key']))
        
        key_rate = compute_secret_key_rate(
            qber=result['qber'],
            detections=result['matching_bases_count'],
            sent_pulses=num_pulses,
            mu=mu_signal
        )
        ir_key_rates.append(key_rate)
    
    return {
        'pns_attack': {
            'mean_qber': np.mean(pns_qbers),
            'std_qber': np.std(pns_qbers),
            'mean_key_length': np.mean(pns_key_lengths),
            'mean_eve_info_gain': np.mean(pns_eve_info),
            'mean_key_rate': np.mean(pns_key_rates)
        },
        'intercept_resend': {
            'mean_qber': np.mean(ir_qbers),
            'std_qber': np.std(ir_qbers),
            'mean_key_length': np.mean(ir_key_lengths),
            'mean_key_rate': np.mean(ir_key_rates)
        },
        'comparison': {
            'qber_difference': np.mean(ir_qbers) - np.mean(pns_qbers),
            'key_rate_difference': np.mean(ir_key_rates) - np.mean(pns_key_rates),
            'pns_advantage': 'PNS' if np.mean(pns_qbers) < np.mean(ir_qbers) else 'IR'
        }
    }