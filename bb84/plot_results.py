"""
Plotting Functions for BB84 Results

Extended with adaptive decoy-state visualizations.
"""

import matplotlib.pyplot as plt
import matplotlib
from typing import List, Dict
import numpy as np

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


def plot_adaptive_qber_evolution(round_results: List[Dict]) -> plt.Figure:
    """
    Plot QBER evolution over adaptive rounds.
    
    RESEARCH VISUALIZATION: Shows adaptation effectiveness
    
    Args:
        round_results: List of round results from adaptive experiment
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    rounds = [r['round'] for r in round_results]
    qbers = [r['qber'] * 100 for r in round_results]
    key_lengths = [r['key_length'] for r in round_results]
    
    # Plot 1: QBER over time
    ax1.plot(rounds, qbers, marker='o', linewidth=2, markersize=6, color='blue', label='QBER')
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    ax1.fill_between(rounds, 0, 11, alpha=0.2, color='green', label='Secure Region')
    ax1.fill_between(rounds, 11, max(qbers + [15]), alpha=0.2, color='red', label='Insecure Region')
    
    ax1.set_xlabel('Round Number', fontsize=12)
    ax1.set_ylabel('QBER (%)', fontsize=12)
    ax1.set_title('QBER Evolution Over Adaptive Rounds', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Key length over time
    ax2.plot(rounds, key_lengths, marker='s', linewidth=2, markersize=6, color='green', label='Key Length')
    ax2.set_xlabel('Round Number', fontsize=12)
    ax2.set_ylabel('Key Length (bits)', fontsize=12)
    ax2.set_title('Key Generation Rate Over Adaptive Rounds', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_decoy_probability_evolution(round_results: List[Dict]) -> plt.Figure:
    """
    Plot decoy probability evolution over rounds.
    
    RESEARCH VISUALIZATION: Shows adaptation dynamics
    
    Args:
        round_results: List of round results from adaptive experiment
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    rounds = [r['round'] for r in round_results]
    signal_probs = [r['signal_prob'] * 100 for r in round_results]
    decoy_probs = [r['decoy_prob'] * 100 for r in round_results]
    vacuum_probs = [r['vacuum_prob'] * 100 for r in round_results]
    
    ax.plot(rounds, signal_probs, marker='o', linewidth=2, label='Signal', color='blue')
    ax.plot(rounds, decoy_probs, marker='s', linewidth=2, label='Decoy', color='orange')
    ax.plot(rounds, vacuum_probs, marker='^', linewidth=2, label='Vacuum', color='green')
    
    ax.set_xlabel('Round Number', fontsize=12)
    ax.set_ylabel('Probability (%)', fontsize=12)
    ax.set_title('Decoy-State Probability Evolution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    return fig


def plot_strategy_comparison(comparison_results: Dict) -> plt.Figure:
    """
    Compare performance of different adaptive strategies.
    
    RESEARCH VISUALIZATION: Strategy benchmarking
    
    Args:
        comparison_results: Results from compare_adaptive_strategies
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    strategies = list(comparison_results.keys())
    mean_qbers = [comparison_results[s]['mean_qber'] * 100 for s in strategies]
    std_qbers = [comparison_results[s]['std_qber'] * 100 for s in strategies]
    mean_key_lengths = [comparison_results[s]['mean_key_length'] for s in strategies]
    std_key_lengths = [comparison_results[s]['std_key_length'] for s in strategies]
    
    # Plot 1: QBER comparison
    x_pos = np.arange(len(strategies))
    ax1.bar(x_pos, mean_qbers, yerr=std_qbers, capsize=5, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(strategies, rotation=15, ha='right')
    ax1.set_ylabel('Mean QBER (%)', fontsize=12)
    ax1.set_title('QBER by Strategy', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Key length comparison
    ax2.bar(x_pos, mean_key_lengths, yerr=std_key_lengths, capsize=5, alpha=0.7, color='lightgreen', edgecolor='black')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(strategies, rotation=15, ha='right')
    ax2.set_ylabel('Mean Key Length (bits)', fontsize=12)
    ax2.set_title('Key Generation by Strategy', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_static_vs_adaptive(comparison_result: Dict) -> plt.Figure:
    """
    Visualize static vs adaptive decoy-state performance.
    
    RESEARCH VISUALIZATION: Core comparison for paper
    
    Args:
        comparison_result: Result from run_static_vs_adaptive_comparison
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    modes = ['Static', 'Adaptive']
    qbers = [
        comparison_result['static']['mean_qber'] * 100,
        comparison_result['adaptive']['mean_qber'] * 100
    ]
    qber_stds = [
        comparison_result['static']['std_qber'] * 100,
        comparison_result['adaptive']['std_qber'] * 100
    ]
    key_lengths = [
        comparison_result['static']['mean_key_length'],
        comparison_result['adaptive']['mean_key_length']
    ]
    key_length_stds = [
        comparison_result['static']['std_key_length'],
        comparison_result['adaptive']['std_key_length']
    ]
    
    # Plot 1: QBER comparison
    x_pos = np.arange(len(modes))
    bars1 = ax1.bar(x_pos, qbers, yerr=qber_stds, capsize=7, 
                    color=['#FF6B6B', '#4ECDC4'], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(modes, fontsize=13, fontweight='bold')
    ax1.set_ylabel('Mean QBER (%)', fontsize=13)
    ax1.set_title('QBER: Static vs Adaptive', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add improvement percentage
    improvement = comparison_result['improvement']['qber_reduction']
    ax1.text(0.5, max(qbers) * 0.9, f'{improvement:+.1f}% improvement', 
             ha='center', fontsize=11, fontweight='bold', 
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Plot 2: Key length comparison
    bars2 = ax2.bar(x_pos, key_lengths, yerr=key_length_stds, capsize=7,
                    color=['#FF6B6B', '#4ECDC4'], alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(modes, fontsize=13, fontweight='bold')
    ax2.set_ylabel('Mean Key Length (bits)', fontsize=13)
    ax2.set_title('Key Generation: Static vs Adaptive', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add improvement percentage
    improvement = comparison_result['improvement']['key_length_increase']
    ax2.text(0.5, max(key_lengths) * 0.9, f'{improvement:+.1f}% improvement',
             ha='center', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    return fig


def plot_key_rate_vs_eve(results: List[Dict]) -> plt.Figure:
    """
    Plot secret key rate vs Eve interception probability.
    
    Args:
        results: List of results from run_eve_sweep_with_key_rate
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    eve_probs = [r['eve_probability'] for r in results]
    mean_key_rates = [r['mean_key_rate'] for r in results]
    std_key_rates = [r['std_key_rate'] for r in results]
    
    # Plot with error bars
    ax.errorbar(eve_probs, mean_key_rates, yerr=std_key_rates,
                marker='o', linewidth=2, markersize=8,
                capsize=5, capthick=2, color='purple', label='Simulated Key Rate')
    
    # Theoretical curve
    from bb84.key_rate_calculator import compute_theoretical_key_rate
    theoretical_rates = [compute_theoretical_key_rate(p) for p in eve_probs]
    ax.plot(eve_probs, theoretical_rates, 'g--', 
            linewidth=2, alpha=0.7, label='Theoretical Key Rate')
    
    # Zero line
    ax.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
    
    # Formatting
    ax.set_xlabel('Eve Interception Probability', fontsize=12)
    ax.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax.set_title('Secret Key Rate vs Eve Probability', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    
    plt.tight_layout()
    return fig


def plot_key_rate_vs_qber(results: List[Dict]) -> plt.Figure:
    """
    Plot secret key rate vs QBER.
    
    Args:
        results: List of results from run_eve_sweep_with_key_rate
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    mean_qbers = [r['mean_qber'] * 100 for r in results]
    mean_key_rates = [r['mean_key_rate'] for r in results]
    
    # Scatter plot
    ax.scatter(mean_qbers, mean_key_rates, s=100, alpha=0.6, 
               c=mean_key_rates, cmap='RdYlGn', edgecolors='black', linewidth=1.5)
    
    # Color bar
    cbar = plt.colorbar(ax.collections[0], ax=ax)
    cbar.set_label('Key Rate (bits/pulse)', fontsize=10)
    
    # QBER threshold
    ax.axvline(x=11, color='red', linestyle='--', linewidth=2, label='Security Threshold (11%)')
    
    # Zero key rate line
    ax.axhline(y=0, color='orange', linestyle=':', linewidth=1.5, alpha=0.5)
    
    # Formatting
    ax.set_xlabel('QBER (%)', fontsize=12)
    ax.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax.set_title('Secret Key Rate vs QBER', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_adaptive_key_rate_evolution(round_results: List[Dict]) -> plt.Figure:
    """
    Plot key rate evolution over adaptive rounds.
    
    Args:
        round_results: List of round results with key_rate field
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    rounds = [r['round'] for r in round_results]
    qbers = [r['qber'] * 100 for r in round_results]
    key_rates = [r['key_rate'] for r in round_results]
    
    # Plot 1: QBER
    ax1.plot(rounds, qbers, marker='o', linewidth=2, markersize=6, color='blue', label='QBER')
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    ax1.set_xlabel('Round Number', fontsize=12)
    ax1.set_ylabel('QBER (%)', fontsize=12)
    ax1.set_title('QBER Evolution', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Key Rate
    ax2.plot(rounds, key_rates, marker='s', linewidth=2, markersize=6, color='green', label='Key Rate')
    ax2.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.5, label='Zero Rate')
    ax2.set_xlabel('Round Number', fontsize=12)
    ax2.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax2.set_title('Secret Key Rate Evolution', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_static_vs_adaptive_key_rate(comparison_result: Dict) -> plt.Figure:
    """
    Compare static vs adaptive key rates.
    
    Args:
        comparison_result: Result from compare_static_adaptive_key_rates
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    modes = ['Static', 'Adaptive']
    key_rates = [
        comparison_result['static']['mean_key_rate'],
        comparison_result['adaptive']['mean_key_rate']
    ]
    key_rate_stds = [
        comparison_result['static']['std_key_rate'],
        comparison_result['adaptive']['std_key_rate']
    ]
    
    x_pos = np.arange(len(modes))
    bars = ax.bar(x_pos, key_rates, yerr=key_rate_stds, capsize=7,
                  color=['#FF6B6B', '#4ECDC4'], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(modes, fontsize=13, fontweight='bold')
    ax.set_ylabel('Mean Secret Key Rate (bits/pulse)', fontsize=13)
    ax.set_title('Secret Key Rate: Static vs Adaptive', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.5)
    
    # Add improvement percentage
    improvement = comparison_result['improvement']['key_rate_increase']
    ax.text(0.5, max(key_rates) * 0.9, f'{improvement:+.1f}% improvement',
            ha='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars, key_rates)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_detection_rates_signal_vs_decoy(results: List[Dict]) -> plt.Figure:
    """
    Plot detection rates for signal vs decoy pulses.
    
    This is crucial for detecting PNS attacks using decoy-state analysis.
    
    Args:
        results: List of PNS experiment results
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    mu_values = [r['mu_signal'] for r in results]
    signal_rates = [r['mean_signal_detection_rate'] for r in results]
    decoy_rates = [r['mean_decoy_detection_rate'] for r in results]
    signal_stds = [r['std_signal_detection_rate'] for r in results]
    decoy_stds = [r['std_decoy_detection_rate'] for r in results]
    
    # Plot with error bars
    ax.errorbar(mu_values, signal_rates, yerr=signal_stds,
                marker='o', linewidth=2, markersize=8,
                capsize=5, label='Signal Pulses', color='blue')
    
    ax.errorbar(mu_values, decoy_rates, yerr=decoy_stds,
                marker='s', linewidth=2, markersize=8,
                capsize=5, label='Decoy Pulses', color='orange')
    
    # Theoretical curves (no attack)
    mu_theory = np.linspace(min(mu_values), max(mu_values), 100)
    # Detection rate ≈ 1 - exp(-η·μ) where η is detector efficiency
    eta = 0.5
    theory_signal = 1 - np.exp(-eta * mu_theory)
    theory_decoy = 1 - np.exp(-eta * 0.1)  # Fixed decoy intensity
    
    ax.plot(mu_theory, theory_signal, '--', color='blue', 
            alpha=0.5, label='Theoretical (no attack)')
    ax.axhline(y=theory_decoy, linestyle='--', color='orange', 
               alpha=0.5)
    
    ax.set_xlabel('Mean Photon Number (μ)', fontsize=12)
    ax.set_ylabel('Detection Rate', fontsize=12)
    ax.set_title('Detection Rate: Signal vs Decoy Pulses (PNS Attack)', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_qber_under_pns(results: List[Dict]) -> plt.Figure:
    """
    Plot QBER under PNS attack vs mean photon number.
    
    Args:
        results: List of PNS experiment results
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    mu_values = [r['mu_signal'] for r in results]
    qbers = [r['mean_qber'] * 100 for r in results]
    qber_stds = [r['std_qber'] * 100 for r in results]
    
    ax.errorbar(mu_values, qbers, yerr=qber_stds,
                marker='o', linewidth=2, markersize=8,
                capsize=5, color='red', label='QBER with PNS')
    
    # Security threshold
    ax.axhline(y=11, color='orange', linestyle='--', 
               linewidth=2, label='Security Threshold (11%)')
    
    ax.set_xlabel('Mean Photon Number (μ)', fontsize=12)
    ax.set_ylabel('QBER (%)', fontsize=12)
    ax.set_title('QBER Under PNS Attack', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_key_rate_under_pns(results: List[Dict]) -> plt.Figure:
    """
    Plot secret key rate under PNS attack.
    
    Args:
        results: List of PNS experiment results
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    mu_values = [r['mu_signal'] for r in results]
    key_rates = [r['mean_key_rate'] for r in results]
    key_rate_stds = [r['std_key_rate'] for r in results]
    
    ax.errorbar(mu_values, key_rates, yerr=key_rate_stds,
                marker='o', linewidth=2, markersize=8,
                capsize=5, color='green', label='Key Rate with PNS')
    
    # Zero line
    ax.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
    
    ax.set_xlabel('Mean Photon Number (μ)', fontsize=12)
    ax.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax.set_title('Secret Key Rate Under PNS Attack', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_eve_information_gain_pns(results: List[Dict]) -> plt.Figure:
    """
    Plot Eve's information gain from PNS attack.
    
    Args:
        results: List of PNS experiment results
    
    Returns:
        Matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    mu_values = [r['mu_signal'] for r in results]
    info_gains = [r['mean_eve_info_gain'] * 100 for r in results]
    info_gain_stds = [r['std_eve_info_gain'] * 100 for r in results]
    
    ax.errorbar(mu_values, info_gains, yerr=info_gain_stds,
                marker='o', linewidth=2, markersize=8,
                capsize=5, color='purple', label="Eve's Information Gain")
    
    # Theoretical multi-photon fraction
    mu_theory = np.linspace(min(mu_values), max(mu_values), 100)
    multi_photon_prob = 1 - np.exp(-mu_theory) * (1 + mu_theory)
    ax.plot(mu_theory, multi_photon_prob * 100, '--', 
            color='purple', alpha=0.5, label='Theoretical (≥2 photons)')
    
    ax.set_xlabel('Mean Photon Number (μ)', fontsize=12)
    ax.set_ylabel("Eve's Information Gain (%)", fontsize=12)
    ax.set_title("Eve's Information Gain from PNS Attack", 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_attack_comparison_ir_vs_pns(comparison_result: Dict) -> plt.Figure:
    """
    Compare Intercept-Resend vs PNS attack.
    
    Args:
        comparison_result: Result from compare_intercept_resend_vs_pns
    
    Returns:
        Matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    attacks = ['Intercept-Resend', 'PNS']
    qbers = [
        comparison_result['intercept_resend']['mean_qber'] * 100,
        comparison_result['pns_attack']['mean_qber'] * 100
    ]
    key_rates = [
        comparison_result['intercept_resend']['mean_key_rate'],
        comparison_result['pns_attack']['mean_key_rate']
    ]
    
    # Plot 1: QBER comparison
    colors = ['#FF6B6B', '#4ECDC4']
    bars1 = ax1.bar(attacks, qbers, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    ax1.set_ylabel('QBER (%)', fontsize=12)
    ax1.set_title('QBER Comparison', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add values on bars
    for bar, qber in zip(bars1, qbers):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{qber:.2f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 2: Key rate comparison
    bars2 = ax2.bar(attacks, key_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
    ax2.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax2.set_title('Key Rate Comparison', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add values on bars
    for bar, rate in zip(bars2, key_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def plot_key_rate_vs_distance(results: List[Dict]) -> plt.Figure:
    """
    Plot secret key rate vs fiber distance.
    
    Args:
        results: Results from run_distance_sweep
    
    Returns:
        Matplotlib Figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    distances = [r['distance_km'] for r in results]
    key_rates = [r['mean_key_rate'] for r in results]
    key_rate_stds = [r['std_key_rate'] for r in results]
    transmittances = [r['transmittance'] for r in results]
    
    # Plot 1: Key rate vs distance
    ax1.errorbar(distances, key_rates, yerr=key_rate_stds,
                 marker='o', linewidth=2, markersize=8,
                 capsize=5, color='blue', label='Simulated')
    
    ax1.axhline(y=0, color='red', linestyle=':', linewidth=1.5)
    ax1.set_xlabel('Fiber Distance (km)', fontsize=12)
    ax1.set_ylabel('Secret Key Rate (bits/pulse)', fontsize=12)
    ax1.set_title('Key Rate vs Distance', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Transmittance vs distance
    ax2.semilogy(distances, transmittances, marker='s', linewidth=2,
                 markersize=8, color='green', label='η = 10^(-0.2L/10)')
    ax2.set_xlabel('Fiber Distance (km)', fontsize=12)
    ax2.set_ylabel('Channel Transmittance η', fontsize=12)
    ax2.set_title('Channel Loss vs Distance', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    return fig


import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
 
 
# --------------------------------
# (A) QBER Stability
# --------------------------------
def plot_qber_stability(results: Dict) -> plt.Figure:
    """
    Plot mean QBER over rounds for each method.
 
    Args:
        results: {method: [{'qber_history': [...], ...}, ...]}
    """
    fig, ax = plt.subplots(figsize=(10, 5))
 
    method_labels = {
        'static':          'Static BB84',
        'adaptive_prng':   'Adaptive (PRNG)',
        'adaptive_chaos':  'Adaptive (Chaotic)',
    }
    colors = {
        'static':          '#888780',
        'adaptive_prng':   '#378ADD',
        'adaptive_chaos':  '#1D9E75',
    }
 
    for method, trials in results.items():
        histories = [t['qber_history'] for t in trials if 'qber_history' in t]
        if not histories:
            continue
 
        # Pad / truncate so every history has the same length
        min_len = min(len(h) for h in histories)
        trimmed = np.array([h[:min_len] for h in histories])
 
        mean_qber = np.mean(trimmed, axis=0)
        std_qber  = np.std(trimmed,  axis=0)
        rounds    = np.arange(1, min_len + 1)
 
        label = method_labels.get(method, method)
        color = colors.get(method, None)
 
        ax.plot(rounds, mean_qber, label=label, color=color, linewidth=2)
        ax.fill_between(rounds,
                        mean_qber - std_qber,
                        mean_qber + std_qber,
                        alpha=0.15, color=color)
 
    ax.axhline(y=0.11, color='red', linestyle='--', linewidth=1.5,
               label='Security threshold (11%)')
    ax.set_title('QBER Stability Comparison', fontsize=14, fontweight='bold')
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('QBER', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
 
 
# --------------------------------
# (B) Attack Detection
# --------------------------------
def plot_attack_detection(results: Dict) -> plt.Figure:
    """
    Plot mean detection rate vs Eve probability for each method.
 
    Args:
        results: {method: {eve_prob: [{'detection_rate': float, ...}, ...]}}
    """
    fig, ax = plt.subplots(figsize=(10, 5))
 
    method_labels = {
        'static':          'Static BB84',
        'adaptive_prng':   'Adaptive (PRNG)',
        'adaptive_chaos':  'Adaptive (Chaotic)',
    }
    markers = {'static': 'o', 'adaptive_prng': 's', 'adaptive_chaos': '^'}
 
    for method, eve_dict in results.items():
        if not isinstance(eve_dict, dict):
            continue
 
        eve_probs  = sorted(eve_dict.keys())
        det_rates  = []
 
        for p in eve_probs:
            trials = eve_dict[p]
            # 'detected' is a bool when eve_present=True, None otherwise
            rates  = []
            for t in trials:
                dr = t.get('detection_rate')
                if dr is None:
                    # Fall back to bool 'detected' if present
                    detected = t.get('detected')
                    dr = float(detected) if detected is not None else 0.0
                rates.append(float(dr))
            det_rates.append(np.mean(rates) if rates else 0.0)
 
        label  = method_labels.get(method, method)
        marker = markers.get(method, 'o')
        ax.plot(eve_probs, det_rates, marker=marker, linewidth=2,
                markersize=7, label=label)
 
    ax.set_title('Attack Detection Rate vs Eve Probability',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Eve Probability', fontsize=12)
    ax.set_ylabel('Detection Rate', fontsize=12)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.10)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
 
 
# --------------------------------
# (C) Key Rate
# --------------------------------
def plot_key_rate(results: Dict) -> plt.Figure:
    """
    Plot mean secret key rate vs Eve probability for each method.
 
    Args:
        results: {method: {eve_prob: [{'mean_key_rate': float, ...}, ...]}}
    """
    fig, ax = plt.subplots(figsize=(10, 5))
 
    method_labels = {
        'static':          'Static BB84',
        'adaptive_prng':   'Adaptive (PRNG)',
        'adaptive_chaos':  'Adaptive (Chaotic)',
    }
    colors  = {'static': '#888780', 'adaptive_prng': '#378ADD',
                'adaptive_chaos': '#1D9E75'}
    markers = {'static': 'o', 'adaptive_prng': 's', 'adaptive_chaos': '^'}
 
    for method, eve_dict in results.items():
        if not isinstance(eve_dict, dict):
            continue
 
        eve_probs  = sorted(eve_dict.keys())
        key_rates  = []
        key_stds   = []
 
        for p in eve_probs:
            trials = eve_dict[p]
            rates  = [t.get('mean_key_rate', 0.0) for t in trials]
            key_rates.append(np.mean(rates))
            key_stds.append(np.std(rates))
 
        label  = method_labels.get(method, method)
        color  = colors.get(method, None)
        marker = markers.get(method, 'o')
 
        ax.errorbar(eve_probs, key_rates, yerr=key_stds,
                    marker=marker, linewidth=2, markersize=7,
                    capsize=4, label=label, color=color)
 
    ax.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.6)
    ax.set_title('Secret Key Rate vs Eve Probability',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Eve Probability', fontsize=12)
    ax.set_ylabel('Mean Secret Key Rate (bits/pulse)', fontsize=12)
    ax.set_xlim(-0.05, 1.05)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
 
 
# --------------------------------
# (D) Adaptability
# --------------------------------
def plot_adaptability(results: Dict) -> plt.Figure:
    """
    Bar chart of mean adaptation speed for adaptive methods.
 
    Args:
        results: {method: [{'adaptability_metrics': {'mean_adaptation_speed': float}, ...}]}
                 Only 'adaptive_prng' and 'adaptive_chaos' keys are expected.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
 
    method_labels = {
        'adaptive_prng':   'Adaptive\n(PRNG)',
        'adaptive_chaos':  'Adaptive\n(Chaotic)',
    }
    colors = {'adaptive_prng': '#378ADD', 'adaptive_chaos': '#1D9E75'}
 
    # Collect only methods that actually exist in results
    methods_present = [m for m in ('adaptive_prng', 'adaptive_chaos')
                       if m in results and results[m]]
 
    speeds = []
    stds   = []
    labels = []
 
    for method in methods_present:
        trial_speeds = []
        for trial in results[method]:
            metrics = trial.get('adaptability_metrics', {})
            speed   = metrics.get('mean_adaptation_speed', 0.0)
            trial_speeds.append(speed)
        speeds.append(np.mean(trial_speeds))
        stds.append(np.std(trial_speeds))
        labels.append(method_labels.get(method, method))
 
    if not speeds:
        ax.text(0.5, 0.5, 'No adaptability data available',
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        fig.tight_layout()
        return fig
 
    x_pos  = np.arange(len(labels))
    bar_colors = [colors.get(m, '#888780') for m in methods_present]
 
    ax.bar(x_pos, speeds, yerr=stds, capsize=6,
           color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel('Mean Adaptation Speed\n(probability change / round)', fontsize=11)
    ax.set_title('Adaptability Comparison', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    return fig