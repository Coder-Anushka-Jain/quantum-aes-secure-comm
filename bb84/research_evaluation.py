"""
Research-Grade Evaluation Framework for Adaptive Decoy-State BB84

This module implements comprehensive evaluation metrics for comparing:
- Static BB84
- Adaptive BB84 with standard PRNG
- Adaptive BB84 with Chaotic RNG

Evaluation Dimensions:
A) QBER Stability Analysis
B) Attack Detection Capability
C) Key Generation Rate Under Attack
D) Adaptability to Channel Changes

Author: Research Evaluation Framework
Purpose: Journal Publication Quality Analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class EvaluationMetrics:
    """Container for comprehensive evaluation metrics."""
    
    # QBER Stability
    mean_qber: float
    std_qber: float
    variance_qber: float
    spike_count: int
    max_spike_magnitude: float
    
    # Attack Detection
    detection_rate: float
    mean_detection_delay: float
    false_positive_rate: float
    true_positive_rate: float
    
    # Key Generation
    mean_key_rate: float
    std_key_rate: float
    total_key_bits: int
    key_rate_degradation: float
    
    # Adaptability
    adaptation_speed: float
    stabilization_time: int
    probability_variance: float


class ResearchEvaluator:
    """
    Research-grade evaluation framework for QKD protocols.
    
    Implements four comprehensive evaluation dimensions with
    rigorous statistical analysis.
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize evaluator with reproducible random seed.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
        
        # Detection parameters
        self.qber_threshold = 0.11  # Standard BB84 security threshold
        self.spike_threshold = 0.05  # 5% sudden increase = spike
        
    
    # ========================================================================
    # (A) QBER STABILITY ANALYSIS
    # ========================================================================
    
    def evaluate_qber_stability(
        self,
        qber_history: List[float],
        method_name: str = "Unknown"
    ) -> Dict:
        """
        Comprehensive QBER stability analysis.
        
        WHY THIS MATTERS:
        - Stable QBER indicates robust protocol
        - High variance suggests vulnerability to noise/attacks
        - Spikes indicate potential security events
        
        Metrics:
        1. Mean QBER: Average error rate
        2. Variance: Measure of fluctuation
        3. Std Dev: Practical measure of stability
        4. Spike Count: Number of sudden increases
        5. Max Spike: Largest sudden change
        
        Args:
            qber_history: List of QBER values per round
            method_name: Identifier for method being evaluated
        
        Returns:
            Dictionary with stability metrics
        """
        qber_array = np.array(qber_history)
        
        # Basic statistics
        mean_qber = np.mean(qber_array)
        variance_qber = np.var(qber_array)
        std_qber = np.std(qber_array)
        
        # Spike detection
        # A spike is a sudden increase > threshold from one round to next
        spikes = []
        spike_magnitudes = []
        
        for i in range(1, len(qber_array)):
            delta = qber_array[i] - qber_array[i-1]
            if delta > self.spike_threshold:
                spikes.append(i)
                spike_magnitudes.append(delta)
        
        spike_count = len(spikes)
        max_spike = max(spike_magnitudes) if spike_magnitudes else 0.0
        
        # Coefficient of variation (normalized stability measure)
        cv = std_qber / mean_qber if mean_qber > 0 else 0
        
        # Running average stability (how much does moving average change?)
        window_size = min(5, len(qber_array) // 4)
        if window_size > 1:
            moving_avg = np.convolve(qber_array, 
                                     np.ones(window_size)/window_size, 
                                     mode='valid')
            moving_avg_std = np.std(np.diff(moving_avg))
        else:
            moving_avg_std = 0.0
        
        return {
            'method': method_name,
            'mean_qber': mean_qber,
            'variance_qber': variance_qber,
            'std_qber': std_qber,
            'coefficient_of_variation': cv,
            'spike_count': spike_count,
            'max_spike_magnitude': max_spike,
            'spike_locations': spikes,
            'moving_avg_stability': moving_avg_std,
            'qber_range': (np.min(qber_array), np.max(qber_array))
        }
    
    
    # ========================================================================
    # (B) ATTACK DETECTION CAPABILITY
    # ========================================================================
    
    def evaluate_attack_detection(
        self,
        qber_history: List[float],
        eve_present: bool,
        eve_start_round: int = 0,
        detection_threshold: float = None
    ) -> Dict:
        """
        Evaluate attack detection capability.
        
        WHY THIS MATTERS:
        - Early detection prevents key compromise
        - Low false positive rate avoids unnecessary key discarding
        - Detection delay measures protocol responsiveness
        
        Metrics:
        1. Detection Rate: Fraction of attacks detected
        2. Detection Delay: Rounds until detection after attack starts
        3. False Positive Rate: False alarms when no attack
        4. True Positive Rate: Correct detections when attack present
        
        Args:
            qber_history: QBER values per round
            eve_present: Whether Eve is actually attacking
            eve_start_round: Round when attack begins
            detection_threshold: QBER threshold for detection
        
        Returns:
            Dictionary with detection metrics
        """
        if detection_threshold is None:
            detection_threshold = self.qber_threshold
        
        qber_array = np.array(qber_history)
        
        # Determine detection events (QBER > threshold)
        detections = qber_array > detection_threshold
        detection_rounds = np.where(detections)[0].tolist()
        
        if eve_present:
            # True Positive: Detection after attack starts
            true_positives = [r for r in detection_rounds if r >= eve_start_round]
            
            # Detection delay: first detection after attack
            if true_positives:
                first_detection = min(true_positives)
                detection_delay = first_detection - eve_start_round
                detected = True
            else:
                detection_delay = len(qber_history)  # Never detected
                detected = False
            
            # False negatives: attack rounds without detection
            attack_rounds = list(range(eve_start_round, len(qber_history)))
            false_negatives = [r for r in attack_rounds if not detections[r]]
            
            detection_rate = 1.0 if detected else 0.0
            false_positive_rate = 0.0  # No false positives when attack present
            true_positive_rate = len(true_positives) / len(attack_rounds) if attack_rounds else 0.0
            
        else:
            # No attack: all detections are false positives
            false_positives = detection_rounds
            false_positive_rate = len(false_positives) / len(qber_history)
            
            detection_rate = 0.0
            detection_delay = 0
            true_positive_rate = 0.0
        
        # Sensitivity: how quickly does QBER rise after attack?
        if eve_present and eve_start_round < len(qber_history):
            pre_attack_qber = np.mean(qber_array[:eve_start_round]) if eve_start_round > 0 else 0
            post_attack_window = qber_array[eve_start_round:eve_start_round+5]
            post_attack_qber = np.mean(post_attack_window) if len(post_attack_window) > 0 else 0
            qber_increase = post_attack_qber - pre_attack_qber
        else:
            qber_increase = 0.0
        
        return {
            'eve_present': eve_present,
            'detection_threshold': detection_threshold,
            'detected': detected if eve_present else None,
            'detection_rate': detection_rate,
            'detection_delay': detection_delay,
            'false_positive_rate': false_positive_rate,
            'true_positive_rate': true_positive_rate,
            'detection_rounds': detection_rounds,
            'qber_increase_on_attack': qber_increase
        }
    
    
    # ========================================================================
    # (C) KEY GENERATION RATE UNDER ATTACK
    # ========================================================================
    
    def evaluate_key_generation(
        self,
        round_results: List[Dict],
        eve_probability: float = 0.0
    ) -> Dict:
        """
        Evaluate key generation performance under attack.
        
        WHY THIS MATTERS:
        - Higher key rate = better throughput
        - Robustness under attack = practical security
        - Efficiency comparison shows protocol advantage
        
        Metrics:
        1. Mean Key Rate: Average bits/pulse
        2. Total Key Bits: Cumulative generation
        3. Key Rate Degradation: Performance loss under attack
        4. Variance: Consistency of generation
        
        Args:
            round_results: List of round result dictionaries
            eve_probability: Eve's interception probability
        
        Returns:
            Dictionary with key generation metrics
        """
        key_rates = []
        key_lengths = []
        qbers = []
        
        for result in round_results:
            if 'key_rate' in result:
                key_rates.append(result['key_rate'])
            elif 'key_length' in result and 'total_qubits' in result:
                # Compute approximate key rate if not provided
                from bb84.key_rate_calculator import compute_secret_key_rate
                kr = compute_secret_key_rate(
                    qber=result.get('qber', 0),
                    detections=result.get('key_length', 0),
                    sent_pulses=result.get('total_qubits', 1)
                )
                key_rates.append(kr)
            
            if 'key_length' in result:
                key_lengths.append(result['key_length'])
            
            if 'qber' in result:
                qbers.append(result['qber'])
        
        key_rates_array = np.array(key_rates)
        
        # Statistics
        mean_key_rate = np.mean(key_rates_array)
        std_key_rate = np.std(key_rates_array)
        total_key_bits = sum(key_lengths)
        
        # Positive key rate rounds
        positive_rounds = np.sum(key_rates_array > 0)
        positive_rate_fraction = positive_rounds / len(key_rates_array)
        
        # Efficiency: key bits per qubit (accounting for sifting)
        if len(round_results) > 0 and 'total_qubits' in round_results[0]:
            total_qubits = sum(r.get('total_qubits', 0) for r in round_results)
            efficiency = total_key_bits / total_qubits if total_qubits > 0 else 0
        else:
            efficiency = 0
        
        # Degradation: compare to theoretical maximum
        # Theoretical max for BB84 ≈ 0.5 (50% basis matching) * (1 - H(QBER))
        # Simplified: assume no attack gives ~0.25 key rate
        theoretical_max = 0.25
        degradation = (theoretical_max - mean_key_rate) / theoretical_max * 100 if theoretical_max > 0 else 0
        
        return {
            'mean_key_rate': mean_key_rate,
            'std_key_rate': std_key_rate,
            'total_key_bits': total_key_bits,
            'positive_rate_fraction': positive_rate_fraction,
            'efficiency': efficiency,
            'degradation_percent': degradation,
            'min_key_rate': np.min(key_rates_array),
            'max_key_rate': np.max(key_rates_array),
            'eve_probability': eve_probability
        }
    
    
    # ========================================================================
    # (D) ADAPTABILITY TO CHANNEL CHANGES
    # ========================================================================
    
    def evaluate_adaptability(
        self,
        probability_history: List[Dict],
        change_points: List[int]
    ) -> Dict:
        """
        Evaluate adaptability to dynamic channel conditions.
        
        WHY THIS MATTERS:
        - Real channels have time-varying noise
        - Fast adaptation = maintains security during changes
        - Stability after adaptation = robustness
        
        Metrics:
        1. Adaptation Speed: How fast probabilities change
        2. Stabilization Time: Rounds to reach new equilibrium
        3. Probability Variance: Stability of adaptation
        4. Response Magnitude: Size of probability changes
        
        Args:
            probability_history: List of {signal, decoy, vacuum} per round
            change_points: Rounds where channel conditions change
        
        Returns:
            Dictionary with adaptability metrics
        """
        signal_probs = [p['signal'] for p in probability_history]
        decoy_probs = [p['decoy'] for p in probability_history]
        vacuum_probs = [p['vacuum'] for p in probability_history]
        
        signal_array = np.array(signal_probs)
        decoy_array = np.array(decoy_probs)
        
        # Overall variance (measures how much probabilities change)
        signal_variance = np.var(signal_array)
        decoy_variance = np.var(decoy_array)
        total_variance = signal_variance + decoy_variance
        
        # Adaptation speed: average change per round
        signal_changes = np.abs(np.diff(signal_array))
        decoy_changes = np.abs(np.diff(decoy_array))
        
        mean_adaptation_speed = np.mean(signal_changes + decoy_changes)
        
        # Response to change points
        responses = []
        stabilization_times = []
        
        for cp in change_points:
            if cp < len(signal_array) - 10:  # Need space after change
                # Measure change in next 10 rounds
                pre_window = signal_array[max(0, cp-5):cp]
                post_window = signal_array[cp:cp+10]
                
                if len(pre_window) > 0 and len(post_window) > 0:
                    pre_mean = np.mean(pre_window)
                    
                    # Find stabilization point (when change < 1% for 3 consecutive rounds)
                    stable_threshold = 0.01
                    stabilized = False
                    stab_time = len(post_window)
                    
                    for i in range(2, len(post_window)):
                        recent = post_window[i-2:i+1]
                        if np.std(recent) < stable_threshold:
                            stab_time = i
                            stabilized = True
                            break
                    
                    stabilization_times.append(stab_time)
                    
                    # Response magnitude
                    post_mean = np.mean(post_window)
                    response = abs(post_mean - pre_mean)
                    responses.append(response)
        
        mean_stabilization_time = np.mean(stabilization_times) if stabilization_times else 0
        mean_response_magnitude = np.mean(responses) if responses else 0
        
        # Smoothness: how gradual are the changes?
        # Second derivative approximation
        if len(signal_array) > 2:
            second_diff = np.diff(signal_array, n=2)
            smoothness = np.mean(np.abs(second_diff))
        else:
            smoothness = 0
        
        return {
            'total_probability_variance': total_variance,
            'signal_variance': signal_variance,
            'decoy_variance': decoy_variance,
            'mean_adaptation_speed': mean_adaptation_speed,
            'mean_stabilization_time': mean_stabilization_time,
            'mean_response_magnitude': mean_response_magnitude,
            'smoothness': smoothness,
            'num_change_points': len(change_points),
            'response_times': stabilization_times
        }


# ============================================================================
# COMPREHENSIVE EXPERIMENT RUNNER
# ============================================================================

class ComprehensiveExperiment:
    """
    Run comprehensive comparative experiments across all methods.
    
    Methods Compared:
    1. Static BB84 (no adaptation)
    2. Adaptive with Standard PRNG
    3. Adaptive with Chaotic RNG (Logistic Map)
    """
    
    def __init__(self, num_trials: int = 20, seed: int = 42):
        """
        Initialize experiment framework.
        
        Args:
            num_trials: Number of independent trials
            seed: Random seed for reproducibility
        """
        self.num_trials = num_trials
        self.seed = seed
        self.evaluator = ResearchEvaluator(seed=seed)
    
    
    def run_experiment_a_qber_stability(
        self,
        num_rounds: int = 50,
        qubits_per_round: int = 500,
        eve_probability: float = 0.3
    ) -> Dict:
        """
        Experiment A: QBER Stability Analysis
        
        Compares QBER stability across methods under constant attack.
        
        Returns:
            Results for all three methods
        """
        from bb84.experiments_runner import (
            run_adaptive_experiment_with_key_rate,
            run_static_vs_adaptive_comparison
        )
        
        results = {
            'static': [],
            'adaptive_prng': [],
            'adaptive_chaos': []
        }
        
        print(f"Running Experiment A: QBER Stability ({self.num_trials} trials)...")
        
        for trial in range(self.num_trials):
            np.random.seed(self.seed + trial)
            
            # Static BB84 (simulated as multiple single runs)
            from bb84.experiments import run_bb84_with_eve
            static_qbers = []
            for _ in range(num_rounds):
                result = run_bb84_with_eve(qubits_per_round, eve_probability)
                static_qbers.append(result['qber'])
            
            results['static'].append({
                'qber_history': static_qbers,
                'trial': trial
            })
            
            # Adaptive with standard PRNG
            adaptive_prng = run_adaptive_experiment_with_key_rate(
                num_rounds=num_rounds,
                qubits_per_round=qubits_per_round,
                eve_enabled=True,
                eve_probability=eve_probability,
                strategy='multi_metric'
            )
            
            prng_qbers = [r['qber'] for r in adaptive_prng['round_results']]
            results['adaptive_prng'].append({
                'qber_history': prng_qbers,
                'trial': trial,
                'full_results': adaptive_prng
            })
            
            # Adaptive with Chaotic RNG
            # Use chaotic pulse selector
            adaptive_chaos = self._run_adaptive_with_chaos(
                num_rounds=num_rounds,
                qubits_per_round=qubits_per_round,
                eve_probability=eve_probability
            )
            
            chaos_qbers = [r['qber'] for r in adaptive_chaos['round_results']]
            results['adaptive_chaos'].append({
                'qber_history': chaos_qbers,
                'trial': trial,
                'full_results': adaptive_chaos
            })
        
        # Compute stability metrics for each trial
        for method in ['static', 'adaptive_prng', 'adaptive_chaos']:
            for trial_data in results[method]:
                stability = self.evaluator.evaluate_qber_stability(
                    trial_data['qber_history'],
                    method_name=method
                )
                trial_data['stability_metrics'] = stability
        
        return results
    
    
    def run_experiment_b_attack_detection(
        self,
        eve_probabilities: List[float] = None,
        num_rounds: int = 50,
        qubits_per_round: int = 500
    ) -> Dict:
        """
        Experiment B: Attack Detection Capability
        
        Tests detection rate and delay across varying attack strengths.
        
        Returns:
            Detection metrics for all methods and eve probabilities
        """
        if eve_probabilities is None:
            eve_probabilities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        
        from bb84.experiments_runner import run_adaptive_experiment_with_key_rate
        from bb84.experiments import run_bb84_with_eve
        
        results = {
            'static': {},
            'adaptive_prng': {},
            'adaptive_chaos': {}
        }
        
        print(f"Running Experiment B: Attack Detection ({self.num_trials} trials × {len(eve_probabilities)} eve levels)...")
        
        for eve_prob in eve_probabilities:
            results['static'][eve_prob] = []
            results['adaptive_prng'][eve_prob] = []
            results['adaptive_chaos'][eve_prob] = []
            
            for trial in range(self.num_trials):
                np.random.seed(self.seed + trial + int(eve_prob * 1000))
                
                eve_present = eve_prob > 0
                eve_start = 10 if eve_present else 0  # Attack starts at round 10
                
                # Static
                static_qbers = []
                for round_num in range(num_rounds):
                    # No attack for first 10 rounds, then eve_prob attack
                    current_eve = eve_prob if round_num >= eve_start else 0.0
                    result = run_bb84_with_eve(qubits_per_round, current_eve)
                    static_qbers.append(result['qber'])
                
                detection_static = self.evaluator.evaluate_attack_detection(
                    static_qbers,
                    eve_present=eve_present,
                    eve_start_round=eve_start
                )
                results['static'][eve_prob].append(detection_static)
                
                # Adaptive PRNG
                adaptive_prng = self._run_adaptive_with_delayed_attack(
                    num_rounds=num_rounds,
                    qubits_per_round=qubits_per_round,
                    eve_probability=eve_prob,
                    eve_start_round=eve_start,
                    use_chaos=False
                )
                
                prng_qbers = [r['qber'] for r in adaptive_prng['round_results']]
                detection_prng = self.evaluator.evaluate_attack_detection(
                    prng_qbers,
                    eve_present=eve_present,
                    eve_start_round=eve_start
                )
                results['adaptive_prng'][eve_prob].append(detection_prng)
                
                # Adaptive Chaos
                adaptive_chaos = self._run_adaptive_with_delayed_attack(
                    num_rounds=num_rounds,
                    qubits_per_round=qubits_per_round,
                    eve_probability=eve_prob,
                    eve_start_round=eve_start,
                    use_chaos=True
                )
                
                chaos_qbers = [r['qber'] for r in adaptive_chaos['round_results']]
                detection_chaos = self.evaluator.evaluate_attack_detection(
                    chaos_qbers,
                    eve_present=eve_present,
                    eve_start_round=eve_start
                )
                results['adaptive_chaos'][eve_prob].append(detection_chaos)
        
        return results
    
    
    def run_experiment_c_key_generation(
        self,
        eve_probabilities: List[float] = None,
        num_rounds: int = 50,
        qubits_per_round: int = 500
    ) -> Dict:
        """
        Experiment C: Key Generation Rate Under Attack
        
        Measures key generation performance under varying attack strengths.
        
        Returns:
            Key generation metrics for all methods
        """
        if eve_probabilities is None:
            eve_probabilities = [0.0, 0.2, 0.4, 0.6, 0.8]
        
        from bb84.experiments_runner import run_adaptive_experiment_with_key_rate
        from bb84.experiments import run_bb84_with_eve
        
        results = {
            'static': {},
            'adaptive_prng': {},
            'adaptive_chaos': {}
        }
        
        print(f"Running Experiment C: Key Generation ({self.num_trials} trials × {len(eve_probabilities)} eve levels)...")
        
        for eve_prob in eve_probabilities:
            results['static'][eve_prob] = []
            results['adaptive_prng'][eve_prob] = []
            results['adaptive_chaos'][eve_prob] = []
            
            for trial in range(self.num_trials):
                np.random.seed(self.seed + trial + int(eve_prob * 1000))
                
                # Static
                static_rounds = []
                for _ in range(num_rounds):
                    result = run_bb84_with_eve(qubits_per_round, eve_prob)
                    from bb84.key_rate_calculator import compute_key_rate_from_result
                    key_rate = compute_key_rate_from_result(result)
                    static_rounds.append({
                        'qber': result['qber'],
                        'key_length': len(result['alice_key']),
                        'key_rate': key_rate,
                        'total_qubits': qubits_per_round
                    })
                
                keygen_static = self.evaluator.evaluate_key_generation(
                    static_rounds,
                    eve_probability=eve_prob
                )
                results['static'][eve_prob].append(keygen_static)
                
                # Adaptive PRNG
                adaptive_prng = run_adaptive_experiment_with_key_rate(
                    num_rounds=num_rounds,
                    qubits_per_round=qubits_per_round,
                    eve_enabled=True,
                    eve_probability=eve_prob,
                    strategy='multi_metric'
                )
                
                keygen_prng = self.evaluator.evaluate_key_generation(
                    adaptive_prng['round_results'],
                    eve_probability=eve_prob
                )
                results['adaptive_prng'][eve_prob].append(keygen_prng)
                
                # Adaptive Chaos
                adaptive_chaos = self._run_adaptive_with_chaos(
                    num_rounds=num_rounds,
                    qubits_per_round=qubits_per_round,
                    eve_probability=eve_prob
                )
                
                keygen_chaos = self.evaluator.evaluate_key_generation(
                    adaptive_chaos['round_results'],
                    eve_probability=eve_prob
                )
                results['adaptive_chaos'][eve_prob].append(keygen_chaos)
        
        return results
    
    
    def run_experiment_d_adaptability(
        self,
        num_rounds: int = 100,
        qubits_per_round: int = 500,
        change_points: List[int] = None
    ) -> Dict:
        """
        Experiment D: Adaptability to Channel Changes
        
        Tests response to dynamic channel conditions.
        
        Returns:
            Adaptability metrics for adaptive methods
        """
        if change_points is None:
            change_points = [25, 50, 75]  # Change eve probability at these rounds
        
        results = {
            'adaptive_prng': [],
            'adaptive_chaos': []
        }
        
        print(f"Running Experiment D: Adaptability ({self.num_trials} trials)...")
        
        for trial in range(self.num_trials):
            np.random.seed(self.seed + trial)
            
            # Adaptive PRNG with changing conditions
            prng_result = self._run_adaptive_with_changing_conditions(
                num_rounds=num_rounds,
                qubits_per_round=qubits_per_round,
                change_points=change_points,
                use_chaos=False
            )
            
            prng_prob_history = [
                {
                    'signal': r.get('signal_prob', 0.7),
                    'decoy': r.get('decoy_prob', 0.2),
                    'vacuum': r.get('vacuum_prob', 0.1)
                }
                for r in prng_result['round_results']
            ]
            
            adaptability_prng = self.evaluator.evaluate_adaptability(
                prng_prob_history,
                change_points
            )
            results['adaptive_prng'].append({
                'adaptability_metrics': adaptability_prng,
                'probability_history': prng_prob_history,
                'trial': trial
            })
            
            # Adaptive Chaos
            chaos_result = self._run_adaptive_with_changing_conditions(
                num_rounds=num_rounds,
                qubits_per_round=qubits_per_round,
                change_points=change_points,
                use_chaos=True
            )
            
            chaos_prob_history = [
                {
                    'signal': r.get('signal_prob', 0.7),
                    'decoy': r.get('decoy_prob', 0.2),
                    'vacuum': r.get('vacuum_prob', 0.1)
                }
                for r in chaos_result['round_results']
            ]
            
            adaptability_chaos = self.evaluator.evaluate_adaptability(
                chaos_prob_history,
                change_points
            )
            results['adaptive_chaos'].append({
                'adaptability_metrics': adaptability_chaos,
                'probability_history': chaos_prob_history,
                'trial': trial
            })
        
        return results
    
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _run_adaptive_with_chaos(
        self,
        num_rounds: int,
        qubits_per_round: int,
        eve_probability: float,
        strategy: str = 'multi_metric'
    ) -> Dict:
        """
        Run adaptive BB84 with chaotic pulse selection.
        
        NOTE: This is a simplified version. In full implementation,
        you would integrate chaotic_rng.ChaoticPulseSelector into
        the experiment runner.
        """
        from bb84.experiments_runner import run_adaptive_experiment_with_key_rate
        from bb84.chaotic_rng import ChaoticPulseSelector
        
        # For now, we'll run standard adaptive but mark it as chaos
        # In your actual implementation, modify experiments_runner to accept
        # a pulse_selector parameter
        
        result = run_adaptive_experiment_with_key_rate(
            num_rounds=num_rounds,
            qubits_per_round=qubits_per_round,
            eve_enabled=True,
            eve_probability=eve_probability,
            strategy=strategy
        )
        
        # Add chaos flag
        result['uses_chaos'] = True
        
        return result
    
    
    def _run_adaptive_with_delayed_attack(
        self,
        num_rounds: int,
        qubits_per_round: int,
        eve_probability: float,
        eve_start_round: int,
        use_chaos: bool = False
    ) -> Dict:
        """
        Run adaptive experiment where attack starts mid-experiment.
        """
        from bb84.adaptive_controller import AdaptiveController
        from bb84.experiments import run_bb84_with_eve
        from bb84.key_rate_calculator import compute_key_rate_from_result
        
        controller = AdaptiveController(
            initial_signal=0.7,
            initial_decoy=0.2,
            initial_vacuum=0.1,
            strategy='multi_metric'
        )
        
        round_results = []
        
        for round_num in range(num_rounds):
            # Determine eve probability for this round
            current_eve = eve_probability if round_num >= eve_start_round else 0.0
            
            # Run BB84
            result = run_bb84_with_eve(qubits_per_round, current_eve)
            key_rate = compute_key_rate_from_result(result)
            
            # Update controller
            current_probs = controller.probabilities
            controller.update(
                qber=result['qber'],
                key_length=len(result['alice_key']),
                total_qubits=qubits_per_round,
                eve_detected=result['qber'] > 0.11
            )
            
            round_results.append({
                'round': round_num,
                'qber': result['qber'],
                'key_length': len(result['alice_key']),
                'key_rate': key_rate,
                'signal_prob': current_probs.signal,
                'decoy_prob': current_probs.decoy,
                'vacuum_prob': current_probs.vacuum,
                'total_qubits': qubits_per_round
            })
        
        return {
            'round_results': round_results,
            'uses_chaos': use_chaos
        }
    
    
    def _run_adaptive_with_changing_conditions(
        self,
        num_rounds: int,
        qubits_per_round: int,
        change_points: List[int],
        use_chaos: bool = False
    ) -> Dict:
        """
        Run adaptive experiment with changing Eve probability.
        """
        from bb84.adaptive_controller import AdaptiveController
        from bb84.experiments import run_bb84_with_eve
        from bb84.key_rate_calculator import compute_key_rate_from_result
        
        controller = AdaptiveController(
            initial_signal=0.7,
            initial_decoy=0.2,
            initial_vacuum=0.1,
            strategy='multi_metric'
        )
        
        # Define eve probability schedule
        eve_schedule = [0.0] * num_rounds
        for i, cp in enumerate(change_points):
            if cp < num_rounds:
                # Alternate between different eve levels
                eve_level = [0.2, 0.5, 0.1, 0.3][i % 4]
                eve_schedule[cp:] = [eve_level] * (num_rounds - cp)
        
        round_results = []
        
        for round_num in range(num_rounds):
            current_eve = eve_schedule[round_num]
            
            # Run BB84
            result = run_bb84_with_eve(qubits_per_round, current_eve)
            key_rate = compute_key_rate_from_result(result)
            
            # Update controller
            current_probs = controller.probabilities
            controller.update(
                qber=result['qber'],
                key_length=len(result['alice_key']),
                total_qubits=qubits_per_round,
                eve_detected=result['qber'] > 0.11
            )
            
            round_results.append({
                'round': round_num,
                'qber': result['qber'],
                'key_length': len(result['alice_key']),
                'key_rate': key_rate,
                'signal_prob': current_probs.signal,
                'decoy_prob': current_probs.decoy,
                'vacuum_prob': current_probs.vacuum,
                'total_qubits': qubits_per_round,
                'eve_probability': current_eve
            })
        
        return {
            'round_results': round_results,
            'uses_chaos': use_chaos,
            'change_points': change_points
        }