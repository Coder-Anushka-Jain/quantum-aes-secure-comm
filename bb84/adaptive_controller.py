"""
Adaptive Decoy-State Controller for BB84 QKD

This module implements dynamic adjustment of decoy-state probabilities based on
observed channel conditions. Supports multiple adaptation strategies for research
comparison.

Research Contributions:
1. Dynamic learning rate adjustment
2. Multi-metric optimization (QBER + key rate)
3. Attack-signature-based adaptation
4. Hybrid static-adaptive mode switching
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DecoyProbabilities:
    """Container for decoy-state probabilities."""
    signal: float
    decoy: float
    vacuum: float
    
    def __post_init__(self):
        """Validate probabilities sum to 1.0"""
        total = self.signal + self.decoy + self.vacuum
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValueError(f"Probabilities must sum to 1.0, got {total}")
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'signal': self.signal,
            'decoy': self.decoy,
            'vacuum': self.vacuum
        }


class AdaptiveController:
    """
    Adaptive decoy-state probability controller with multiple strategies.
    
    Strategies:
    - 'qber_based': Traditional QBER-only adaptation
    - 'multi_metric': Combined QBER + key rate optimization
    - 'attack_aware': Attack-signature-based response
    - 'hybrid': Intelligent static/adaptive switching
    """
    
    def __init__(
        self,
        initial_signal: float = 0.70,
        initial_decoy: float = 0.20,
        initial_vacuum: float = 0.10,
        strategy: str = 'qber_based',
        learning_rate: float = 0.1,
        qber_threshold: float = 0.11,
        min_signal: float = 0.40,
        max_signal: float = 0.85,
        min_decoy: float = 0.10,
        max_decoy: float = 0.50
    ):
        """
        Initialize adaptive controller.
        
        Args:
            initial_signal: Starting signal probability
            initial_decoy: Starting decoy probability
            initial_vacuum: Starting vacuum probability
            strategy: Adaptation strategy ('qber_based', 'multi_metric', 'attack_aware', 'hybrid')
            learning_rate: Base learning rate for updates
            qber_threshold: Security threshold for QBER
            min_signal: Minimum allowed signal probability
            max_signal: Maximum allowed signal probability
            min_decoy: Minimum allowed decoy probability
            max_decoy: Maximum allowed decoy probability
        """
        self.probabilities = DecoyProbabilities(initial_signal, initial_decoy, initial_vacuum)
        self.strategy = strategy
        self.base_learning_rate = learning_rate
        self.qber_threshold = qber_threshold
        self.min_signal = min_signal
        self.max_signal = max_signal
        self.min_decoy = min_decoy
        self.max_decoy = max_decoy
        
        # History tracking for adaptive learning rate
        self.qber_history = []
        self.key_rate_history = []
        self.probability_history = []
        
        # Attack detection state
        self.attack_detected = False
        self.attack_type = None
        
        # Hybrid mode state
        self.static_mode = False
        self.rounds_since_change = 0
        
    def update(
        self,
        qber: float,
        key_length: int,
        total_qubits: int,
        eve_detected: bool = False
    ) -> DecoyProbabilities:
        """
        Update decoy probabilities based on observed metrics.
        
        Args:
            qber: Observed quantum bit error rate
            key_length: Length of final key generated
            total_qubits: Total qubits transmitted
            eve_detected: Whether eavesdropping was detected
        
        Returns:
            Updated DecoyProbabilities
        """
        # Record history
        self.qber_history.append(qber)
        key_rate = key_length / total_qubits if total_qubits > 0 else 0
        self.key_rate_history.append(key_rate)
        self.probability_history.append(self.probabilities.to_dict())
        
        # Select strategy
        if self.strategy == 'qber_based':
            new_probs = self._qber_based_update(qber)
        elif self.strategy == 'multi_metric':
            new_probs = self._multi_metric_update(qber, key_rate)
        elif self.strategy == 'attack_aware':
            new_probs = self._attack_aware_update(qber, eve_detected)
        elif self.strategy == 'hybrid':
            new_probs = self._hybrid_update(qber, key_rate)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        self.probabilities = new_probs
        return self.probabilities
    
    def _qber_based_update(self, qber: float) -> DecoyProbabilities:
        """
        Strategy 1: Traditional QBER-based adaptation.
        
        Logic:
        - High QBER → Increase decoy (better attack detection)
        - Low QBER → Increase signal (better key rate)
        """
        learning_rate = self._compute_adaptive_learning_rate()
        
        # Compute QBER deviation from threshold
        qber_deviation = qber - self.qber_threshold
        
        # Update signal probability (inverse relationship with QBER)
        signal_delta = -learning_rate * qber_deviation
        new_signal = self.probabilities.signal + signal_delta
        new_signal = np.clip(new_signal, self.min_signal, self.max_signal)
        
        # Update decoy probability (direct relationship with QBER)
        decoy_delta = learning_rate * qber_deviation
        new_decoy = self.probabilities.decoy + decoy_delta
        new_decoy = np.clip(new_decoy, self.min_decoy, self.max_decoy)
        
        # Normalize and compute vacuum
        total = new_signal + new_decoy
        if total > 1.0:
            # Rescale to fit
            new_signal = new_signal / total * 0.95
            new_decoy = new_decoy / total * 0.95
        
        new_vacuum = 1.0 - new_signal - new_decoy
        new_vacuum = max(0.05, new_vacuum)  # Minimum 5% vacuum
        
        # Final normalization
        total = new_signal + new_decoy + new_vacuum
        new_signal /= total
        new_decoy /= total
        new_vacuum /= total
        
        return DecoyProbabilities(new_signal, new_decoy, new_vacuum)
    
    def _multi_metric_update(self, qber: float, key_rate: float) -> DecoyProbabilities:
        """
        Strategy 2: Multi-metric optimization (QBER + key rate).
        
        RESEARCH CONTRIBUTION: Balances security and throughput
        
        Logic:
        - Optimize composite score: α·(1-QBER/threshold) + β·key_rate
        - Higher weight on security when QBER is high
        """
        learning_rate = self._compute_adaptive_learning_rate()
        
        # Dynamic weight adjustment
        if qber > self.qber_threshold:
            alpha = 0.8  # Prioritize security
            beta = 0.2
        else:
            alpha = 0.4  # Balance security and throughput
            beta = 0.6
        
        # Security score (higher is better)
        security_score = 1.0 - (qber / (self.qber_threshold * 2))
        security_score = np.clip(security_score, 0, 1)
        
        # Composite objective
        composite_score = alpha * security_score + beta * key_rate
        
        # Update based on composite score
        # Low score → more decoy (defensive)
        # High score → more signal (aggressive)
        score_deviation = composite_score - 0.5  # 0.5 is neutral
        
        signal_delta = learning_rate * score_deviation
        new_signal = self.probabilities.signal + signal_delta
        new_signal = np.clip(new_signal, self.min_signal, self.max_signal)
        
        decoy_delta = -learning_rate * score_deviation * 0.7
        new_decoy = self.probabilities.decoy + decoy_delta
        new_decoy = np.clip(new_decoy, self.min_decoy, self.max_decoy)
        
        new_vacuum = 1.0 - new_signal - new_decoy
        new_vacuum = max(0.05, new_vacuum)
        
        # Normalize
        total = new_signal + new_decoy + new_vacuum
        return DecoyProbabilities(
            new_signal / total,
            new_decoy / total,
            new_vacuum / total
        )
    
    def _attack_aware_update(self, qber: float, eve_detected: bool) -> DecoyProbabilities:
        """
        Strategy 3: Attack-signature-based adaptation.
        
        RESEARCH CONTRIBUTION: Different responses for different attack patterns
        
        Attack signatures:
        - Sudden QBER spike → PNS attack → Increase vacuum
        - Gradual QBER increase → Intercept-resend → Increase decoy
        - QBER oscillation → Adaptive attack → Increase all decoys
        """
        learning_rate = self._compute_adaptive_learning_rate()
        
        # Detect attack pattern
        attack_type = self._detect_attack_signature(qber)
        
        if attack_type == 'sudden_spike':
            # PNS attack suspected → increase vacuum
            new_signal = self.probabilities.signal * 0.9
            new_decoy = self.probabilities.decoy * 1.1
            new_vacuum = self.probabilities.vacuum * 1.3
            
        elif attack_type == 'gradual_increase':
            # Intercept-resend → increase decoy
            new_signal = self.probabilities.signal * 0.95
            new_decoy = self.probabilities.decoy * 1.2
            new_vacuum = self.probabilities.vacuum
            
        elif attack_type == 'oscillation':
            # Adaptive attack → defensive posture
            new_signal = self.min_signal
            new_decoy = self.max_decoy
            new_vacuum = 1.0 - new_signal - new_decoy
            
        else:
            # No attack → optimize for key rate
            new_signal = min(self.probabilities.signal * 1.05, self.max_signal)
            new_decoy = max(self.probabilities.decoy * 0.95, self.min_decoy)
            new_vacuum = 1.0 - new_signal - new_decoy
        
        # Normalize
        total = new_signal + new_decoy + new_vacuum
        return DecoyProbabilities(
            new_signal / total,
            new_decoy / total,
            new_vacuum / total
        )
    
    def _hybrid_update(self, qber: float, key_rate: float) -> DecoyProbabilities:
        """
        Strategy 4: Hybrid static-adaptive switching.
        
        RESEARCH CONTRIBUTION: Reduces computational overhead
        
        Logic:
        - Switch to static mode when channel is stable
        - Switch to adaptive mode when instability detected
        """
        # Detect channel stability
        is_stable = self._is_channel_stable()
        
        if is_stable and not self.static_mode:
            # Switch to static mode
            self.static_mode = True
            self.rounds_since_change = 0
            return self.probabilities  # Keep current
        
        elif not is_stable and self.static_mode:
            # Switch to adaptive mode
            self.static_mode = False
            self.rounds_since_change = 0
        
        # If in static mode, don't update
        if self.static_mode:
            self.rounds_since_change += 1
            return self.probabilities
        
        # If in adaptive mode, use multi-metric strategy
        self.rounds_since_change += 1
        return self._multi_metric_update(qber, key_rate)
    
    def _compute_adaptive_learning_rate(self) -> float:
        """
        RESEARCH CONTRIBUTION: Dynamic learning rate based on QBER volatility.
        
        Logic:
        - High QBER variance → smaller learning rate (cautious)
        - Low QBER variance → larger learning rate (aggressive)
        """
        if len(self.qber_history) < 3:
            return self.base_learning_rate
        
        # Compute QBER volatility (std dev of recent history)
        recent_qber = self.qber_history[-5:]
        volatility = np.std(recent_qber)
        
        # Inverse relationship: high volatility → low learning rate
        adaptive_lr = self.base_learning_rate * np.exp(-5 * volatility)
        adaptive_lr = np.clip(adaptive_lr, 0.01, 0.3)
        
        return adaptive_lr
    
    def _detect_attack_signature(self, current_qber: float) -> Optional[str]:
        """
        Detect attack pattern from QBER history.
        
        Returns:
            Attack type: 'sudden_spike', 'gradual_increase', 'oscillation', or None
        """
        if len(self.qber_history) < 3:
            return None
        
        recent_qber = np.array(self.qber_history[-5:])
        
        # Sudden spike: large single-round increase
        if len(recent_qber) >= 2:
            last_delta = recent_qber[-1] - recent_qber[-2]
            if last_delta > 0.05:  # 5% sudden increase
                return 'sudden_spike'
        
        # Gradual increase: consistent upward trend
        if len(recent_qber) >= 4:
            trend = np.polyfit(range(len(recent_qber)), recent_qber, 1)[0]
            if trend > 0.01:  # Positive trend
                return 'gradual_increase'
        
        # Oscillation: high variance
        if len(recent_qber) >= 5:
            variance = np.var(recent_qber)
            if variance > 0.01:  # High variance
                return 'oscillation'
        
        return None
    
    def _is_channel_stable(self) -> bool:
        """
        Determine if channel is stable (for hybrid mode).
        
        Stability criteria:
        - QBER variance < threshold
        - Key rate variance < threshold
        - No recent attacks detected
        """
        if len(self.qber_history) < 10:
            return False
        
        recent_qber = self.qber_history[-10:]
        recent_key_rate = self.key_rate_history[-10:]
        
        qber_stable = np.std(recent_qber) < 0.02
        key_rate_stable = np.std(recent_key_rate) < 0.05
        no_attacks = all(q < self.qber_threshold for q in recent_qber[-5:])
        
        return qber_stable and key_rate_stable and no_attacks
    
    def get_statistics(self) -> Dict:
        """
        Get controller statistics for analysis.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.qber_history:
            return {}
        
        return {
            'mean_qber': np.mean(self.qber_history),
            'std_qber': np.std(self.qber_history),
            'mean_key_rate': np.mean(self.key_rate_history),
            'std_key_rate': np.std(self.key_rate_history),
            'current_learning_rate': self._compute_adaptive_learning_rate(),
            'rounds_executed': len(self.qber_history),
            'static_mode': self.static_mode if self.strategy == 'hybrid' else None,
            'attack_detected': self.attack_detected
        }
    
    def reset(self):
        """Reset controller to initial state."""
        self.__init__(
            initial_signal=self.probabilities.signal,
            initial_decoy=self.probabilities.decoy,
            initial_vacuum=self.probabilities.vacuum,
            strategy=self.strategy,
            learning_rate=self.base_learning_rate
        )