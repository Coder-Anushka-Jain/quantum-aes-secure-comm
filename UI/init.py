"""
Streamlit UI Package for BB84 Quantum-Classical Secure Communication
"""

"""
BB84 Quantum Key Distribution Package
"""

from .bb84_core import bb84_protocol
from .eve_attack import eve_intercept_resend
from .experiments import run_bb84, run_bb84_with_eve
from .experiments_runner import run_experiment, run_eve_sweep
from .key_rate_calculator import (
    binary_entropy, compute_secret_key_rate, 
    compute_key_rate_from_result, analyze_key_rate_statistics
)

__all__ = [
    'bb84_protocol',
    'eve_intercept_resend',
    'run_bb84',
    'run_bb84_with_eve',
    'run_experiment',
    'run_eve_sweep',
    'binary_entropy',
    'compute_secret_key_rate',
    'compute_key_rate_from_result',
    'analyze_key_rate_statistics'
]