"""
Distance-Dependent QKD Experiments

Analyze how secret key rate degrades with distance for different
adaptive strategies.
"""

import numpy as np
from typing import List, Dict
from .channel_model import FiberChannel
from .experiments import run_bb84_with_eve
from .adaptive_controller import AdaptiveController
from .key_rate_calculator import compute_secret_key_rate


def run_distance_sweep(
    distances_km: List[float],
    num_qubits: int = 1000,
    eve_probability: float = 0.0,
    mu_signal: float = 0.5,
    dark_count_rate: float = 1e-6,
    trials: int = 5
) -> List[Dict]:
    """
    Sweep across different fiber distances.
    
    Args:
        distances_km: List of distances to test
        num_qubits: Qubits per experiment
        eve_probability: Eve's interception probability
        mu_signal: Mean photon number
        dark_count_rate: Dark count rate
        trials: Trials per distance
    
    Returns:
        List of results for each distance
    """
    results = []
    
    for distance in distances_km:
        # Create channel model
        channel = FiberChannel(
            distance_km=distance,
            fiber_loss_db_per_km=0.2,
            detector_efficiency=0.5,
            dark_count_rate=dark_count_rate
        )
        
        trial_qbers = []
        trial_key_rates = []
        trial_detections = []
        
        for _ in range(trials):
            # Run BB84 with channel model
            result = run_bb84_with_channel(
                num_qubits=num_qubits,
                eve_probability=eve_probability,
                channel=channel,
                mu_signal=mu_signal
            )
            
            trial_qbers.append(result['qber'])
            trial_key_rates.append(result['key_rate'])
            trial_detections.append(result['detections'])
        
        results.append({
            'distance_km': distance,
            'transmittance': channel.transmittance,
            'mean_qber': np.mean(trial_qbers),
            'std_qber': np.std(trial_qbers),
            'mean_key_rate': np.mean(trial_key_rates),
            'std_key_rate': np.std(trial_key_rates),
            'mean_detections': np.mean(trial_detections),
            'channel_params': channel.get_parameters()
        })
    
    return results


def run_bb84_with_channel(
    num_qubits: int,
    eve_probability: float,
    channel: FiberChannel,
    mu_signal: float = 0.5
) -> Dict:
    """
    Run BB84 with realistic channel model.
    
    Args:
        num_qubits: Number of qubits
        eve_probability: Eve's interception probability
        channel: FiberChannel object
        mu_signal: Mean photon number
    
    Returns:
        Results dictionary
    """
    # Alice's preparation
    alice_bits = np.random.randint(0, 2, num_qubits)
    alice_bases = np.random.randint(0, 2, num_qubits)
    
    # Photon number sampling (Poisson distribution)
    photon_numbers = np.random.poisson(mu_signal, num_qubits)
    
    # Apply channel loss
    transmitted_photons = [channel.apply_channel_loss(n) for n in photon_numbers]
    
    # Bob's measurement
    bob_bases = np.random.randint(0, 2, num_qubits)
    bob_detections = []
    bob_bits = []
    dark_counts = 0
    
    for n_photons, alice_basis, bob_basis, alice_bit in zip(
        transmitted_photons, alice_bases, bob_bases, alice_bits
    ):
        # Detection with dark counts
        detected, is_dark = channel.detect_photons(n_photons)
        
        if detected:
            if is_dark:
                dark_counts += 1
                # Dark count gives random bit
                bob_bit = np.random.randint(0, 2)
            else:
                # Real photon detection
                if alice_basis == bob_basis:
                    # Matching bases
                    bob_bit = alice_bit
                else:
                    # Non-matching bases
                    bob_bit = np.random.randint(0, 2)
            
            bob_detections.append(True)
            bob_bits.append(bob_bit)
        else:
            bob_detections.append(False)
            bob_bits.append(None)
    
    # Basis reconciliation
    matching_bases = alice_bases == bob_bases
    detected_and_matching = [
        det and match for det, match in zip(bob_detections, matching_bases)
    ]
    
    # Sifted key
    alice_sifted = alice_bits[detected_and_matching]
    bob_sifted = np.array([
        bob_bits[i] for i in range(num_qubits) if detected_and_matching[i]
    ])
    
    # QBER
    if len(alice_sifted) > 0:
        errors = np.sum(alice_sifted != bob_sifted)
        qber = errors / len(alice_sifted)
    else:
        qber = 1.0
    
    # Key rate
    detections = len(alice_sifted)
    key_rate = compute_secret_key_rate(
        qber=qber,
        detections=detections,
        sent_pulses=num_qubits,
        mu=mu_signal
    )
    
    return {
        'qber': qber,
        'alice_key': alice_sifted.tolist(),
        'bob_key': bob_sifted.tolist(),
        'key_rate': key_rate,
        'detections': detections,
        'dark_counts': dark_counts,
        'total_qubits': num_qubits
    }


def compare_strategies_vs_distance(
    distances_km: List[float],
    strategies: List[str],
    num_rounds: int = 20,
    qubits_per_round: int = 500,
    eve_probability: float = 0.2,
    trials: int = 3
) -> Dict:
    """
    Compare adaptive strategies across different distances.
    
    Args:
        distances_km: List of distances to test
        strategies: List of adaptive strategies
        num_rounds: Rounds per experiment
        qubits_per_round: Qubits per round
        eve_probability: Eve's interception probability
        trials: Trials per configuration
    
    Returns:
        Comparison results
    """
    from .experiments_runner import run_adaptive_experiment_with_key_rate
    
    results = {}
    
    for strategy in strategies:
        strategy_results = []
        
        for distance in distances_km:
            channel = FiberChannel(distance_km=distance)
            
            trial_key_rates = []
            trial_qbers = []
            
            for _ in range(trials):
                # Run adaptive experiment with channel
                result = run_adaptive_with_channel(
                    num_rounds=num_rounds,
                    qubits_per_round=qubits_per_round,
                    eve_probability=eve_probability,
                    channel=channel,
                    strategy=strategy
                )
                
                # Extract final metrics
                final_key_rates = [r['key_rate'] for r in result['round_results']]
                final_qbers = [r['qber'] for r in result['round_results']]
                
                trial_key_rates.append(np.mean(final_key_rates))
                trial_qbers.append(np.mean(final_qbers))
            
            strategy_results.append({
                'distance_km': distance,
                'transmittance': channel.transmittance,
                'mean_key_rate': np.mean(trial_key_rates),
                'std_key_rate': np.std(trial_key_rates),
                'mean_qber': np.mean(trial_qbers)
            })
        
        results[strategy] = strategy_results
    
    return results


def run_adaptive_with_channel(
    num_rounds: int,
    qubits_per_round: int,
    eve_probability: float,
    channel: FiberChannel,
    strategy: str = 'multi_metric',
    mu_signal: float = 0.5
) -> Dict:
    """
    Run adaptive experiment with channel model.
    
    Args:
        num_rounds: Number of rounds
        qubits_per_round: Qubits per round
        eve_probability: Eve's probability
        channel: FiberChannel object
        strategy: Adaptive strategy
        mu_signal: Mean photon number
    
    Returns:
        Experiment results
    """
    controller = AdaptiveController(
        initial_signal=0.7,
        initial_decoy=0.2,
        initial_vacuum=0.1,
        strategy=strategy
    )
    
    round_results = []
    
    for round_num in range(num_rounds):
        # Run BB84 with channel
        result = run_bb84_with_channel(
            num_qubits=qubits_per_round,
            eve_probability=eve_probability,
            channel=channel,
            mu_signal=mu_signal
        )
        
        # Update controller
        controller.update(
            qber=result['qber'],
            key_length=result['detections'],
            total_qubits=qubits_per_round,
            eve_detected=result['qber'] > 0.11
        )
        
        round_results.append({
            'round': round_num,
            'qber': result['qber'],
            'key_rate': result['key_rate'],
            'detections': result['detections']
        })
    
    return {
        'strategy': strategy,
        'round_results': round_results,
        'channel_params': channel.get_parameters()
    }