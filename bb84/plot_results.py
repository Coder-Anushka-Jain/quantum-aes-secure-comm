"""
Plotting Functions for BB84 Results

This module provides matplotlib-based visualization functions that return
Figure objects compatible with Streamlit.
"""

import matplotlib.pyplot as plt
import matplotlib
from typing import List, Dict

# Use non-interactive backend for Streamlit compatibility
matplotlib.use('Agg')


def plot_qber(qber: float) -> plt.Figure:
    """
    Create a visual representation of QBER with security threshold.
    
    Args:
        qber: Quantum Bit Error Rate (0.0 to 1.0)
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Security threshold for BB84 is typically 11%
    threshold = 0.11
    
    # Create bar chart
    colors = ['green' if qber <= threshold else 'red']
    bars = ax.bar(['QBER'], [qber * 100], color=colors, alpha=0.7, edgecolor='black')
    
    # Add threshold line
    ax.axhline(y=threshold * 100, color='orange', linestyle='--', 
               linewidth=2, label=f'Security Threshold ({threshold*100:.0f}%)')
    
    # Formatting
    ax.set_ylabel('Error Rate (%)', fontsize=12)
    ax.set_title('Quantum Bit Error Rate (QBER)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(25, qber * 100 + 5))
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value label on bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_qber_vs_eve(results: List[Dict]) -> plt.Figure:
    """
    Plot QBER as a function of Eve's interception probability.
    
    Args:
        results: List of experiment results from run_eve_sweep
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    eve_probs = [r['eve_probability'] for r in results]
    mean_qbers = [r['mean_qber'] * 100 for r in results]
    std_qbers = [r['std_qber'] * 100 for r in results]
    
    # Plot with error bars
    ax.errorbar(eve_probs, mean_qbers, yerr=std_qbers, 
                marker='o', linewidth=2, markersize=8, 
                capsize=5, capthick=2, label='Measured QBER')
    
    # Add security threshold
    ax.axhline(y=11, color='red', linestyle='--', 
               linewidth=2, label='Security Threshold (11%)')
    
    # Theoretical QBER = 0.25 * eve_probability
    theoretical_qber = [25 * p for p in eve_probs]
    ax.plot(eve_probs, theoretical_qber, 'g--', 
            linewidth=2, alpha=0.7, label='Theoretical (25% × p)')
    
    # Formatting
    ax.set_xlabel('Eve Interception Probability', fontsize=12)
    ax.set_ylabel('QBER (%)', fontsize=12)
    ax.set_title('QBER vs Eve Interception Probability', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    
    plt.tight_layout()
    return fig


def plot_key_length_vs_eve(results: List[Dict]) -> plt.Figure:
    """
    Plot final key length as a function of Eve's interception probability.
    
    Args:
        results: List of experiment results from run_eve_sweep
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    eve_probs = [r['eve_probability'] for r in results]
    mean_lengths = [r['mean_key_length'] for r in results]
    std_lengths = [r['std_key_length'] for r in results]
    
    # Plot with error bars
    ax.errorbar(eve_probs, mean_lengths, yerr=std_lengths,
                marker='s', linewidth=2, markersize=8,
                capsize=5, capthick=2, color='blue', label='Final Key Length')
    
    # Formatting
    ax.set_xlabel('Eve Interception Probability', fontsize=12)
    ax.set_ylabel('Key Length (bits)', fontsize=12)
    ax.set_title('Final Key Length vs Eve Interception Probability', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    
    plt.tight_layout()
    return fig