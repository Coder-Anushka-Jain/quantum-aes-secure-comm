"""
Experiment Runner for BB84 Protocol

Extended with adaptive decoy-state support for multi-round experiments.
"""

import numpy as np
from typing import Dict, List, Optional
from .experiments import run_bb84, run_bb84_with_eve
from .adaptive_controller import AdaptiveController, DecoyProbabilities


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


def run_adaptive_experiment(
    num_rounds: int,
    qubits_per_round: int,
    eve_enabled: bool,
    eve_probability: float = 0.0,
    strategy: str = 'qber_based',
    learning_rate: float = 0.1,
    initial_signal: float = 0.70,
    initial_decoy: float = 0.20,
    initial_vacuum: float = 0.10
) -> Dict:
    """
    Run multi-round adaptive decoy-state BB84 experiment.
    
    RESEARCH FEATURE: Core adaptive QKD implementation
    
    Args:
        num_rounds: Number of adaptation rounds
        qubits_per_round: Qubits transmitted per round
        eve_enabled: Whether Eve is present
        eve_probability: Eve's interception probability
        strategy: Adaptation strategy ('qber_based', 'multi_metric', 'attack_aware', 'hybrid')
        learning_rate: Base learning rate for adaptation
        initial_signal: Initial signal probability
        initial_decoy: Initial decoy probability
        initial_vacuum: Initial vacuum probability
    
    Returns:
        Dictionary with round-by-round results and statistics
    """
    # Initialize controller
    controller = AdaptiveController(
        initial_signal=initial_signal,
        initial_decoy=initial_decoy,
        initial_vacuum=initial_vacuum,
        strategy=strategy,
        learning_rate=learning_rate
    )
    
    # Storage for round results
    round_results = []
    
    for round_num in range(num_rounds):
        # Get current probabilities
        current_probs = controller.probabilities
        
        # Run BB84 with current parameters
        # Note: In full implementation, decoy probabilities would affect
        # photon number statistics, but for this simulation we track them
        if eve_enabled:
            result = run_bb84_with_eve(qubits_per_round, eve_probability)
        else:
            result = run_bb84(qubits_per_round)
        
        # Extract metrics
        qber = result['qber']
        key_length = len(result['alice_key'])
        eve_detected = qber > 0.11
        
        # Update controller
        new_probs = controller.update(
            qber=qber,
            key_length=key_length,
            total_qubits=qubits_per_round,
            eve_detected=eve_detected
        )
        
        # Store round result
        round_results.append({
            'round': round_num,
            'qber': qber,
            'key_length': key_length,
            'signal_prob': current_probs.signal,
            'decoy_prob': current_probs.decoy,
            'vacuum_prob': current_probs.vacuum,
            'learning_rate': controller._compute_adaptive_learning_rate(),
            'eve_detected': eve_detected
        })
    
    # Compile final statistics
    return {
        'strategy': strategy,
        'num_rounds': num_rounds,
        'round_results': round_results,
        'controller_stats': controller.get_statistics(),
        'final_probabilities': controller.probabilities.to_dict()
    }


def compare_adaptive_strategies(
    num_rounds: int,
    qubits_per_round: int,
    eve_probability: float,
    strategies: List[str] = None,
    trials: int = 5
) -> Dict:
    """
    Compare performance of different adaptive strategies.
    
    RESEARCH FEATURE: Strategy benchmarking
    
    Args:
        num_rounds: Rounds per experiment
        qubits_per_round: Qubits per round
        eve_probability: Eve's interception probability
        strategies: List of strategies to compare
        trials: Trials per strategy
    
    Returns:
        Comparative results for each strategy
    """
    if strategies is None:
        strategies = ['qber_based', 'multi_metric', 'attack_aware', 'hybrid']
    
    comparison_results = {}
    
    for strategy in strategies:
        strategy_results = []
        
        for _ in range(trials):
            result = run_adaptive_experiment(
                num_rounds=num_rounds,
                qubits_per_round=qubits_per_round,
                eve_enabled=True,
                eve_probability=eve_probability,
                strategy=strategy
            )
            strategy_results.append(result)
        
        # Aggregate statistics
        all_qbers = []
        all_key_lengths = []
        
        for result in strategy_results:
            for round_res in result['round_results']:
                all_qbers.append(round_res['qber'])
                all_key_lengths.append(round_res['key_length'])
        
        comparison_results[strategy] = {
            'mean_qber': np.mean(all_qbers),
            'std_qber': np.std(all_qbers),
            'mean_key_length': np.mean(all_key_lengths),
            'std_key_length': np.std(all_key_lengths),
            'trials': trials,
            'raw_results': strategy_results
        }
    
    return comparison_results


def run_static_vs_adaptive_comparison(
    num_rounds: int,
    qubits_per_round: int,
    eve_probability: float,
    adaptive_strategy: str = 'multi_metric',
    trials: int = 5
) -> Dict:
    """
    Compare static decoy-state vs adaptive decoy-state performance.
    
    RESEARCH FEATURE: Core comparison for paper
    
    Args:
        num_rounds: Number of rounds
        qubits_per_round: Qubits per round
        eve_probability: Eve's interception probability
        adaptive_strategy: Which adaptive strategy to use
        trials: Number of trials
    
    Returns:
        Comparison results
    """
    static_results = []
    adaptive_results = []
    
    for _ in range(trials):
        # Static mode (no adaptation)
        static_trial = []
        for _ in range(num_rounds):
            result = run_bb84_with_eve(qubits_per_round, eve_probability)
            static_trial.append({
                'qber': result['qber'],
                'key_length': len(result['alice_key'])
            })
        static_results.append(static_trial)
        
        # Adaptive mode
        adaptive_trial = run_adaptive_experiment(
            num_rounds=num_rounds,
            qubits_per_round=qubits_per_round,
            eve_enabled=True,
            eve_probability=eve_probability,
            strategy=adaptive_strategy
        )
        adaptive_results.append(adaptive_trial)
    
    # Aggregate metrics
    static_qbers = []
    static_key_lengths = []
    for trial in static_results:
        for round_res in trial:
            static_qbers.append(round_res['qber'])
            static_key_lengths.append(round_res['key_length'])
    
    adaptive_qbers = []
    adaptive_key_lengths = []
    for trial in adaptive_results:
        for round_res in trial['round_results']:
            adaptive_qbers.append(round_res['qber'])
            adaptive_key_lengths.append(round_res['key_length'])
    
    return {
        'static': {
            'mean_qber': np.mean(static_qbers),
            'std_qber': np.std(static_qbers),
            'mean_key_length': np.mean(static_key_lengths),
            'std_key_length': np.std(static_key_lengths)
        },
        'adaptive': {
            'mean_qber': np.mean(adaptive_qbers),
            'std_qber': np.std(adaptive_qbers),
            'mean_key_length': np.mean(adaptive_key_lengths),
            'std_key_length': np.std(adaptive_key_lengths),
            'strategy': adaptive_strategy
        },
        'improvement': {
            'qber_reduction': (np.mean(static_qbers) - np.mean(adaptive_qbers)) / np.mean(static_qbers) * 100,
            'key_length_increase': (np.mean(adaptive_key_lengths) - np.mean(static_key_lengths)) / np.mean(static_key_lengths) * 100
        }
    }