"""
Chaotic Random Number Generators for QKD

Implements chaos-based PRNGs for enhanced unpredictability in pulse selection.

Supports:
- Logistic Map
- Lorenz System
- Henon Map
- Includes NIST randomness testing
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import Counter


class ChaoticRNG:
    """Base class for chaotic random number generators."""
    
    def __init__(self, seed: float = None):
        """Initialize chaotic RNG."""
        if seed is None:
            seed = np.random.random()
        self.seed = seed
        self.state = seed
    
    def generate(self, n: int) -> np.ndarray:
        """Generate n random numbers. Override in subclass."""
        raise NotImplementedError
    
    def generate_discrete(self, n: int, num_classes: int = 3) -> np.ndarray:
        """
        Generate discrete random numbers in range [0, num_classes-1].
        
        Args:
            n: Number of samples
            num_classes: Number of discrete classes
        
        Returns:
            Array of discrete random integers
        """
        continuous = self.generate(n)
        # Map [0,1] to discrete classes
        discrete = np.floor(continuous * num_classes).astype(int)
        # Clip to ensure valid range
        discrete = np.clip(discrete, 0, num_classes - 1)
        return discrete


class LogisticMap(ChaoticRNG):
    """
    Logistic Map: x_{n+1} = r * x_n * (1 - x_n)
    
    Chaotic for r ≈ 3.57 to 4.0
    Most chaotic at r = 4.0
    """
    
    def __init__(self, r: float = 3.99, seed: float = None):
        """
        Initialize logistic map.
        
        Args:
            r: Control parameter (3.57 < r ≤ 4 for chaos)
            seed: Initial condition (0 < seed < 1)
        """
        super().__init__(seed)
        self.r = r
        if self.r <= 3.57 or self.r > 4.0:
            print(f"Warning: r={r} may not be in chaotic regime (3.57 < r ≤ 4)")
    
    def generate(self, n: int) -> np.ndarray:
        """Generate n chaotic random numbers."""
        sequence = np.zeros(n)
        x = self.state
        
        for i in range(n):
            x = self.r * x * (1 - x)
            sequence[i] = x
        
        self.state = x
        return sequence


class LorenzSystem(ChaoticRNG):
    """
    Lorenz System:
    dx/dt = σ(y - x)
    dy/dt = x(ρ - z) - y
    dz/dt = xy - βz
    
    Classic chaotic attractor with σ=10, ρ=28, β=8/3
    """
    
    def __init__(self, sigma: float = 10.0, rho: float = 28.0, 
                 beta: float = 8/3, dt: float = 0.01, seed: float = None):
        """
        Initialize Lorenz system.
        
        Args:
            sigma: Prandtl number
            rho: Rayleigh number
            beta: Geometric parameter
            dt: Time step for integration
            seed: Initial condition
        """
        super().__init__(seed)
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = dt
        
        # Initial state (x, y, z)
        self.x = 1.0
        self.y = 1.0
        self.z = 1.0 + self.seed
    
    def _step(self):
        """Perform one integration step (Euler method)."""
        dx = self.sigma * (self.y - self.x)
        dy = self.x * (self.rho - self.z) - self.y
        dz = self.x * self.y - self.beta * self.z
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
    
    def generate(self, n: int) -> np.ndarray:
        """Generate n random numbers from Lorenz x-coordinate."""
        sequence = np.zeros(n)
        
        # Burn-in period to reach attractor
        for _ in range(100):
            self._step()
        
        # Generate sequence
        for i in range(n):
            self._step()
            # Normalize x to [0, 1]
            # Lorenz x typically in [-20, 20]
            normalized = (self.x + 20) / 40
            normalized = np.clip(normalized, 0, 1)
            sequence[i] = normalized
        
        return sequence


class HenonMap(ChaoticRNG):
    """
    Henon Map:
    x_{n+1} = 1 - a*x_n^2 + y_n
    y_{n+1} = b*x_n
    
    Chaotic for a=1.4, b=0.3
    """
    
    def __init__(self, a: float = 1.4, b: float = 0.3, seed: float = None):
        """
        Initialize Henon map.
        
        Args:
            a: Parameter a (typically 1.4)
            b: Parameter b (typically 0.3)
            seed: Initial condition
        """
        super().__init__(seed)
        self.a = a
        self.b = b
        self.x = self.seed
        self.y = self.seed * 0.5
    
    def generate(self, n: int) -> np.ndarray:
        """Generate n chaotic random numbers."""
        sequence = np.zeros(n)
        
        for i in range(n):
            x_new = 1 - self.a * self.x**2 + self.y
            y_new = self.b * self.x
            
            self.x = x_new
            self.y = y_new
            
            # Normalize to [0, 1]
            # Henon x typically in [-1.5, 1.5]
            normalized = (self.x + 1.5) / 3.0
            normalized = np.clip(normalized, 0, 1)
            sequence[i] = normalized
        
        return sequence


class ChaoticPulseSelector:
    """
    Chaotic pulse type selector for decoy-state BB84.
    
    Uses chaotic RNG with probability normalization.
    """
    
    def __init__(
        self,
        rng_type: str = 'logistic',
        signal_prob: float = 0.7,
        decoy_prob: float = 0.2,
        vacuum_prob: float = 0.1,
        **rng_params
    ):
        """
        Initialize chaotic pulse selector.
        
        Args:
            rng_type: 'logistic', 'lorenz', or 'henon'
            signal_prob: Target signal probability
            decoy_prob: Target decoy probability
            vacuum_prob: Target vacuum probability
            **rng_params: Parameters for chaotic RNG
        """
        # Normalize probabilities
        total = signal_prob + decoy_prob + vacuum_prob
        self.signal_prob = signal_prob / total
        self.decoy_prob = decoy_prob / total
        self.vacuum_prob = vacuum_prob / total
        
        # Create chaotic RNG
        if rng_type == 'logistic':
            self.rng = LogisticMap(**rng_params)
        elif rng_type == 'lorenz':
            self.rng = LorenzSystem(**rng_params)
        elif rng_type == 'henon':
            self.rng = HenonMap(**rng_params)
        else:
            raise ValueError(f"Unknown RNG type: {rng_type}")
        
        self.rng_type = rng_type
    
    def generate_pulse_types(self, n: int) -> np.ndarray:
        """
        Generate n pulse types using chaotic RNG.
        
        Returns:
            Array of pulse types: 0=signal, 1=decoy, 2=vacuum
        """
        # Generate chaotic random numbers
        random_values = self.rng.generate(n)
        
        # Map to pulse types using cumulative probabilities
        pulse_types = np.zeros(n, dtype=int)
        
        for i in range(n):
            r = random_values[i]
            if r < self.signal_prob:
                pulse_types[i] = 0  # Signal
            elif r < self.signal_prob + self.decoy_prob:
                pulse_types[i] = 1  # Decoy
            else:
                pulse_types[i] = 2  # Vacuum
        
        return pulse_types
    
    def get_actual_probabilities(self, pulse_types: np.ndarray) -> Dict:
        """
        Compute actual probabilities from generated sequence.
        
        Args:
            pulse_types: Generated pulse type array
        
        Returns:
            Dictionary with actual probabilities
        """
        counts = Counter(pulse_types)
        total = len(pulse_types)
        
        return {
            'signal': counts[0] / total,
            'decoy': counts[1] / total,
            'vacuum': counts[2] / total,
            'total': total
        }


def test_randomness_chi_square(sequence: np.ndarray, num_bins: int = 10) -> Dict:
    """
    Perform chi-square test for uniformity.
    
    Args:
        sequence: Random sequence in [0, 1]
        num_bins: Number of bins
    
    Returns:
        Test results
    """
    # Bin the data
    counts, _ = np.histogram(sequence, bins=num_bins, range=(0, 1))
    
    # Expected count per bin
    expected = len(sequence) / num_bins
    
    # Chi-square statistic
    chi_square = np.sum((counts - expected)**2 / expected)
    
    # Degrees of freedom
    dof = num_bins - 1
    
    # Critical value at 95% confidence (approximate)
    critical_value = 16.919  # for dof=9
    
    passed = chi_square < critical_value
    
    return {
        'chi_square': chi_square,
        'critical_value': critical_value,
        'dof': dof,
        'passed': passed,
        'counts': counts.tolist(),
        'expected': expected
    }


def test_randomness_runs(sequence: np.ndarray) -> Dict:
    """
    Perform runs test for independence.
    
    A run is a sequence of consecutive values above/below median.
    
    Args:
        sequence: Random sequence
    
    Returns:
        Test results
    """
    median = np.median(sequence)
    above_median = (sequence > median).astype(int)
    
    # Count runs
    runs = 1
    for i in range(1, len(above_median)):
        if above_median[i] != above_median[i-1]:
            runs += 1
    
    # Expected runs and variance
    n = len(sequence)
    n1 = np.sum(above_median)
    n0 = n - n1
    
    expected_runs = (2 * n0 * n1) / n + 1
    variance_runs = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n**2 * (n - 1))
    
    # Z-score
    if variance_runs > 0:
        z_score = (runs - expected_runs) / np.sqrt(variance_runs)
    else:
        z_score = 0
    
    # Test at 95% confidence: |z| < 1.96
    passed = abs(z_score) < 1.96
    
    return {
        'runs': runs,
        'expected_runs': expected_runs,
        'z_score': z_score,
        'passed': passed
    }


def comprehensive_randomness_test(rng: ChaoticRNG, n: int = 10000) -> Dict:
    """
    Perform comprehensive randomness testing.
    
    Args:
        rng: Chaotic RNG instance
        n: Number of samples to test
    
    Returns:
        Test results
    """
    sequence = rng.generate(n)
    
    chi_square_result = test_randomness_chi_square(sequence)
    runs_result = test_randomness_runs(sequence)
    
    # Statistical properties
    mean = np.mean(sequence)
    std = np.std(sequence)
    
    return {
        'rng_type': type(rng).__name__,
        'n_samples': n,
        'mean': mean,
        'std': std,
        'chi_square_test': chi_square_result,
        'runs_test': runs_result,
        'overall_passed': chi_square_result['passed'] and runs_result['passed']
    }