"""
Streamlit Application for BB84 + AES Secure Communication System

Extended with:
- Adaptive Decoy-State QKD
- Secret Key Rate Analysis
- PNS Attack Analysis
- Distance-Dependent Analysis
- Chaotic Random Number Generators
"""

import sys
import os
from pathlib import Path

# THIS MUST BE FIRST — before any bb84 imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now these will work
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from bb84.research_evaluation import ComprehensiveExperiment
from bb84.plot_results import (
    plot_qber_stability,
    plot_attack_detection,
    plot_key_rate,
    plot_adaptability
)

from bb84.experiments_runner import (
    run_experiment, run_eve_sweep, run_adaptive_experiment,
    compare_adaptive_strategies, run_static_vs_adaptive_comparison,
    run_eve_sweep_with_key_rate, run_adaptive_experiment_with_key_rate,
    compare_static_adaptive_key_rates
)
from bb84.plot_results import (
    plot_qber, plot_qber_vs_eve, plot_key_length_vs_eve,
    plot_adaptive_qber_evolution, plot_decoy_probability_evolution,
    plot_strategy_comparison, plot_static_vs_adaptive,
    plot_key_rate_vs_eve, plot_key_rate_vs_qber,
    plot_adaptive_key_rate_evolution, plot_static_vs_adaptive_key_rate,
    plot_detection_rates_signal_vs_decoy, plot_qber_under_pns,
    plot_key_rate_under_pns, plot_eve_information_gain_pns,
    plot_attack_comparison_ir_vs_pns,
    plot_key_rate_vs_distance,
    plot_qber_stability,
    plot_attack_detection,
    plot_key_rate,
    plot_adaptability
)
from bb84.key_rate_calculator import compute_key_rate_from_result
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib


# Page configuration
st.set_page_config(
    page_title="Advanced BB84 Quantum-Classical Secure Communication",
    page_icon="🔐",
    layout="wide"
)


def derive_aes_key(quantum_key: list) -> bytes:
    """Derive a 128-bit AES key from the quantum key using SHA-256."""
    key_string = ''.join(str(bit) for bit in quantum_key)
    hash_obj = hashlib.sha256(key_string.encode())
    aes_key = hash_obj.digest()[:16]
    return aes_key


def encrypt_message(message: str, key: bytes) -> tuple:
    """Encrypt a message using AES-128 in CBC mode."""
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return ct_bytes, cipher.iv


def decrypt_message(ciphertext: bytes, key: bytes, iv: bytes) -> str:
    """Decrypt a message using AES-128 in CBC mode."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return pt.decode('utf-8')


def main():
    # Title
    st.title("🔐 Advanced BB84 Quantum-Classical Secure Communication")
    st.markdown("""
    ### Research-Grade Quantum Cryptography Simulator
    **Features:** Adaptive Decoy States • Secret Key Rate Analysis • PNS Attack Detection • 
    Distance-Dependent Modeling • Chaotic Random Number Generators
    """)
    
    st.divider()
    
    # Sidebar - Mode Selection
    st.sidebar.header("🎛️ Mode Selection")
    
    mode = st.sidebar.radio(
    "Operation Mode",
    [
        "Single Run", "Adaptive Multi-Round", "Strategy Comparison", 
        "Static vs Adaptive", "Key Rate Analysis", "PNS Attack Analysis",
        "Distance Analysis", "Chaotic RNG Analysis",
        "Research Evaluation (Journal)"   # 🔥 ADD THIS
    ]
)
    
    st.sidebar.divider()
    
    # Common parameters
    st.sidebar.header("⚙️ Common Parameters")
    
    num_qubits = st.sidebar.slider(
        "Qubits per Round",
        min_value=100,
        max_value=2000,
        value=500,
        step=100
    )
    
    eve_enabled = st.sidebar.checkbox("Enable Eve (Eavesdropper)", value=True)
    
    eve_probability = 0.0
    if eve_enabled:
        eve_probability = st.sidebar.slider(
            "Eve Interception Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05
        )
    
    # Mode-specific parameters
    if mode == "Single Run":
        run_single_mode(num_qubits, eve_enabled, eve_probability)
    
    elif mode == "Adaptive Multi-Round":
        run_adaptive_mode(num_qubits, eve_enabled, eve_probability)
    
    elif mode == "Strategy Comparison":
        run_strategy_comparison_mode(num_qubits, eve_probability)
    
    elif mode == "Static vs Adaptive":
        run_static_vs_adaptive_mode(num_qubits, eve_probability)
    
    elif mode == "Key Rate Analysis":
        run_key_rate_analysis_mode(num_qubits)
    
    elif mode == "PNS Attack Analysis":
        run_pns_attack_mode(num_qubits)
    
    elif mode == "Distance Analysis":
        run_distance_analysis_mode(num_qubits, eve_probability)
    
    elif mode == "Chaotic RNG Analysis":
        run_chaotic_rng_mode(num_qubits)

    elif mode == "Research Evaluation (Journal)":
        run_research_evaluation_mode(num_qubits)


def run_single_mode(num_qubits, eve_enabled, eve_probability):
    """Single-run BB84 execution (original functionality)."""
    
    message_input = st.sidebar.text_input(
        "Message to Encrypt",
        value="Quantum cryptography is secure!",
        help="Message to encrypt with quantum-derived AES key"
    )
    
    run_button = st.sidebar.button("🚀 Run BB84 Protocol", type="primary")
    
    if run_button or 'last_result' in st.session_state:
        
        if run_button:
            with st.spinner("Running BB84 protocol..."):
                result = run_experiment(num_qubits, eve_enabled, eve_probability)
                st.session_state.last_result = result
        else:
            result = st.session_state.last_result
        
        # Display results
        st.header("1️⃣ BB84 Protocol Execution")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Qubits Sent", result['total_qubits'])
        with col2:
            st.metric("Matching Bases", result['matching_bases_count'])
        with col3:
            st.metric("Final Key Length", len(result['alice_key']))
        with col4:
            if eve_enabled:
                st.metric("Eve Interceptions", result.get('eve_interceptions', 'N/A'))
            else:
                st.metric("Eve Status", "Not Present")
        
        # QBER Analysis
        st.header("2️⃣ QBER & Security Analysis")
        qber_value = result['qber']
        qber_percent = qber_value * 100
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("QBER", f"{qber_percent:.2f}%")
            threshold = 11.0
            if qber_percent <= threshold:
                st.success(f"✅ Secure: QBER ≤ {threshold}%")
            else:
                st.error(f"⚠️ Insecure: QBER > {threshold}%")
        
        with col2:
            fig_qber = plot_qber(qber_value)
            st.pyplot(fig_qber)
        
        # Key Preview
        st.header("3️⃣ Quantum Key Preview")
        alice_key = result['alice_key']
        bob_key = result['bob_key']
        
        if len(alice_key) >= 64:
            preview_bits = 64
            st.text("Alice's Key (first 64 bits):")
            st.code(''.join(str(b) for b in alice_key[:preview_bits]))
            st.text("Bob's Key (first 64 bits):")
            st.code(''.join(str(b) for b in bob_key[:preview_bits]))
        
        # AES Encryption
        st.header("4️⃣ AES-128 Encryption")
        if len(alice_key) >= 128:
            aes_key = derive_aes_key(alice_key[:256] if len(alice_key) >= 256 else alice_key)
            st.code(aes_key.hex())
            
            ciphertext, iv = encrypt_message(message_input, aes_key)
            decrypted_message = decrypt_message(ciphertext, aes_key, iv)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Original:**")
                st.info(message_input)
            with col2:
                st.markdown("**Encrypted:**")
                st.code(ciphertext.hex()[:50] + "...")
            with col3:
                st.markdown("**Decrypted:**")
                st.success(decrypted_message)
        
        # Secret Key Rate Analysis
        st.header("5️⃣ Secret Key Rate Analysis")
        
        key_rate = compute_key_rate_from_result(result)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Secret Key Rate", f"{key_rate:.6f} bits/pulse")
            if key_rate > 0:
                st.success("✅ Positive key rate: Secure key generation possible")
            else:
                st.error("❌ Zero key rate: Cannot generate secure keys")
        
        with col2:
            with st.expander("ℹ️ Key Rate Formula"):
                st.latex(r"R = Q_1(1 - H(e_1)) - Q_\mu f H(E_\mu)")
                st.markdown("""
                **Where:**
                - Q₁ = Single-photon gain ≈ Qμ × exp(-μ)
                - e₁ = Single-photon error rate ≈ QBER
                - Qμ = Overall gain = detections / sent_pulses
                - Eμ = Overall QBER
                - f = Error correction efficiency (1.16)
                - μ = Mean photon number (0.5)
                - H(x) = Binary entropy = -x log₂(x) - (1-x) log₂(1-x)
                
                **Interpretation:**
                - Positive R: Secure key can be extracted
                - R ≈ 0: Marginal security
                - R < 0: Communication is insecure
                """)


def run_adaptive_mode(num_qubits, eve_enabled, eve_probability):
    """Adaptive multi-round execution with decoy-state optimization."""
    
    st.sidebar.header("🔄 Adaptive Parameters")
    
    num_rounds = st.sidebar.slider("Number of Rounds", 5, 50, 20, 5)
    
    strategy = st.sidebar.selectbox(
        "Adaptation Strategy",
        ["qber_based", "multi_metric", "attack_aware", "hybrid"],
        help="Select adaptation algorithm"
    )
    
    learning_rate = st.sidebar.slider(
        "Base Learning Rate",
        0.01, 0.3, 0.1, 0.01,
        help="Controls adaptation speed"
    )
    
    # Initial decoy probabilities
    with st.sidebar.expander("Initial Decoy Probabilities"):
        init_signal = st.slider("Signal", 0.4, 0.85, 0.70, 0.05)
        init_decoy = st.slider("Decoy", 0.1, 0.5, 0.20, 0.05)
        init_vacuum = 1.0 - init_signal - init_decoy
        st.metric("Vacuum (auto)", f"{init_vacuum:.2f}")
    
    # Key rate parameters
    with st.sidebar.expander("⚙️ Key Rate Parameters"):
        mu = st.slider("Mean Photon Number (μ)", 0.1, 1.0, 0.5, 0.1)
        f = st.slider("Error Correction Efficiency (f)", 1.0, 1.5, 1.16, 0.01)
    
    run_button = st.sidebar.button("🚀 Run Adaptive Experiment", type="primary")
    
    if run_button:
        with st.spinner(f"Running {num_rounds} adaptive rounds..."):
            result = run_adaptive_experiment_with_key_rate(
                num_rounds=num_rounds,
                qubits_per_round=num_qubits,
                eve_enabled=eve_enabled,
                eve_probability=eve_probability,
                strategy=strategy,
                learning_rate=learning_rate,
                initial_signal=init_signal,
                initial_decoy=init_decoy,
                initial_vacuum=init_vacuum,
                mu=mu,
                f=f
            )
            st.session_state.adaptive_result = result
    
    if 'adaptive_result' in st.session_state:
        result = st.session_state.adaptive_result
        
        # Summary Metrics
        st.header("📊 Adaptive Experiment Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Strategy", result['strategy'])
        with col2:
            st.metric("Total Rounds", result['num_rounds'])
        with col3:
            mean_qber = result['controller_stats']['mean_qber'] * 100
            st.metric("Mean QBER", f"{mean_qber:.2f}%")
        with col4:
            mean_key_rate_controller = result['controller_stats']['mean_key_rate']
            st.metric("Mean Key Rate", f"{mean_key_rate_controller:.3f}")
        
        # Final Probabilities
        st.header("🎯 Final Decoy Probabilities")
        final_probs = result['final_probabilities']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Signal", f"{final_probs['signal']:.3f}")
        with col2:
            st.metric("Decoy", f"{final_probs['decoy']:.3f}")
        with col3:
            st.metric("Vacuum", f"{final_probs['vacuum']:.3f}")
        
        # Key Rate Metrics
        st.header("💎 Secret Key Rate Performance")
        
        key_rate_stats = result.get('key_rate_stats', {})
        col1, col2, col3 = st.columns(3)
        with col1:
            mean_rate = key_rate_stats.get('mean', 0)
            st.metric("Mean Key Rate", f"{mean_rate:.6f} bits/pulse")
        with col2:
            std_rate = key_rate_stats.get('std', 0)
            st.metric("Std Key Rate", f"{std_rate:.6f}")
        with col3:
            pos_fraction = key_rate_stats.get('positive_rate_fraction', 0) * 100
            st.metric("Positive Rate %", f"{pos_fraction:.1f}%")
        
        # Visualizations
        st.header("📈 Adaptive Evolution")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_qber_evo = plot_adaptive_qber_evolution(result['round_results'])
            st.pyplot(fig_qber_evo)
        
        with col2:
            fig_prob_evo = plot_decoy_probability_evolution(result['round_results'])
            st.pyplot(fig_prob_evo)
        
        # Key rate evolution
        st.header("🔑 Key Rate Evolution")
        fig_key_rate_evo = plot_adaptive_key_rate_evolution(result['round_results'])
        st.pyplot(fig_key_rate_evo)
        
        # Detailed Round Data
        with st.expander("📋 Detailed Round-by-Round Data"):
            import pandas as pd
            df = pd.DataFrame(result['round_results'])
            df['qber'] = df['qber'] * 100
            df = df.round(6)
            st.dataframe(df, use_container_width=True)


def run_strategy_comparison_mode(num_qubits, eve_probability):
    """Compare different adaptive strategies."""
    
    st.sidebar.header("🔬 Comparison Parameters")
    
    num_rounds = st.sidebar.slider("Rounds per Trial", 5, 30, 15, 5)
    trials = st.sidebar.slider("Trials per Strategy", 1, 10, 3, 1)
    
    strategies = st.sidebar.multiselect(
        "Strategies to Compare",
        ["qber_based", "multi_metric", "attack_aware", "hybrid"],
        default=["qber_based", "multi_metric", "attack_aware"]
    )
    
    run_button = st.sidebar.button("🚀 Run Comparison", type="primary")
    
    if run_button and strategies:
        with st.spinner("Comparing strategies..."):
            result = compare_adaptive_strategies(
                num_rounds=num_rounds,
                qubits_per_round=num_qubits,
                eve_probability=eve_probability,
                strategies=strategies,
                trials=trials
            )
            st.session_state.comparison_result = result
    
    if 'comparison_result' in st.session_state:
        result = st.session_state.comparison_result
        
        st.header("🏆 Strategy Performance Comparison")
        
        # Performance table
        import pandas as pd
        summary_data = []
        for strategy, stats in result.items():
            summary_data.append({
                'Strategy': strategy,
                'Mean QBER (%)': stats['mean_qber'] * 100,
                'Std QBER (%)': stats['std_qber'] * 100,
                'Mean Key Length': stats['mean_key_length'],
                'Std Key Length': stats['std_key_length']
            })
        df = pd.DataFrame(summary_data)
        st.dataframe(df.round(3), use_container_width=True)
        
        # Visualization
        fig_comparison = plot_strategy_comparison(result)
        st.pyplot(fig_comparison)
        
        # Winner determination
        best_qber_strategy = min(result.items(), key=lambda x: x[1]['mean_qber'])[0]
        best_key_strategy = max(result.items(), key=lambda x: x[1]['mean_key_length'])[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🥇 Best QBER: **{best_qber_strategy}**")
        with col2:
            st.success(f"🥇 Best Key Rate: **{best_key_strategy}**")


def run_static_vs_adaptive_mode(num_qubits, eve_probability):
    """Compare static vs adaptive decoy-state performance."""
    
    st.sidebar.header("⚖️ Comparison Parameters")
    
    num_rounds = st.sidebar.slider("Rounds per Mode", 10, 50, 25, 5)
    trials = st.sidebar.slider("Trials", 1, 10, 5, 1)
    
    adaptive_strategy = st.sidebar.selectbox(
        "Adaptive Strategy",
        ["multi_metric", "qber_based", "attack_aware", "hybrid"],
        help="Strategy for adaptive mode"
    )
    
    # Key rate parameters
    with st.sidebar.expander("⚙️ Key Rate Parameters"):
        mu = st.slider("Mean Photon Number (μ)", 0.1, 1.0, 0.5, 0.1)
        f = st.slider("Error Correction Efficiency (f)", 1.0, 1.5, 1.16, 0.01)
    
    run_button = st.sidebar.button("🚀 Run Comparison", type="primary")
    
    if run_button:
        with st.spinner("Running static vs adaptive comparison..."):
            result = compare_static_adaptive_key_rates(
                num_rounds=num_rounds,
                qubits_per_round=num_qubits,
                eve_probability=eve_probability,
                adaptive_strategy=adaptive_strategy,
                trials=trials,
                mu=mu,
                f=f
            )
            st.session_state.sva_result = result
    
    if 'sva_result' in st.session_state:
        result = st.session_state.sva_result
        
        st.header("📊 Static vs Adaptive Performance")
        
        # Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 Static Mode")
            st.metric("Mean QBER", f"{result['static']['mean_qber']*100:.2f}%")
            st.metric("Mean Key Length", f"{result['static']['mean_key_length']:.0f} bits")
            st.metric("Mean Key Rate", f"{result['static']['mean_key_rate']:.6f} bits/pulse")
        
        with col2:
            st.subheader("🔄 Adaptive Mode")
            st.metric("Mean QBER", f"{result['adaptive']['mean_qber']*100:.2f}%")
            st.metric("Mean Key Length", f"{result['adaptive']['mean_key_length']:.0f} bits")
            st.metric("Mean Key Rate", f"{result['adaptive']['mean_key_rate']:.6f} bits/pulse")
        
        # Improvement metrics
        st.header("📈 Performance Improvement")
        col1, col2, col3 = st.columns(3)
        with col1:
            qber_improvement = result['improvement']['qber_reduction']
            st.metric("QBER Reduction", f"{qber_improvement:.1f}%", 
                     delta=f"{qber_improvement:.1f}%", delta_color="inverse")
        with col2:
            key_improvement = result['improvement']['key_length_increase']
            st.metric("Key Length Increase", f"{key_improvement:.1f}%",
                     delta=f"{key_improvement:.1f}%")
        with col3:
            rate_improvement = result['improvement']['key_rate_increase']
            st.metric("Key Rate Increase", f"{rate_improvement:.1f}%",
                     delta=f"{rate_improvement:.1f}%")
        
        # Visualizations
        st.header("📊 Performance Comparison Plots")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_sva = plot_static_vs_adaptive(result)
            st.pyplot(fig_sva)
        
        with col2:
            fig_key_rate = plot_static_vs_adaptive_key_rate(result)
            st.pyplot(fig_key_rate)
        
        # Research interpretation
        with st.expander("📝 Research Interpretation"):
            st.markdown(f"""
            ### Key Findings
            
            **QBER Performance:**
            - Static mode achieved {result['static']['mean_qber']*100:.2f}% QBER
            - Adaptive mode achieved {result['adaptive']['mean_qber']*100:.2f}% QBER
            - **Improvement: {qber_improvement:.1f}%**
            
            **Key Generation:**
            - Static mode: {result['static']['mean_key_length']:.0f} bits average
            - Adaptive mode: {result['adaptive']['mean_key_length']:.0f} bits average
            - **Improvement: {key_improvement:.1f}%**
            
            **Secret Key Rate:**
            - Static mode: {result['static']['mean_key_rate']:.6f} bits/pulse
            - Adaptive mode: {result['adaptive']['mean_key_rate']:.6f} bits/pulse
            - **Improvement: {rate_improvement:.1f}%**
            
            **Conclusion:**
            The adaptive {adaptive_strategy} strategy demonstrates 
            {'superior' if qber_improvement > 0 else 'comparable'} performance
            to static decoy-state allocation, with particular strength in
            {'QBER minimization' if abs(qber_improvement) > abs(rate_improvement) else 'key rate optimization'}.
            
            The secret key rate improvement of {rate_improvement:.1f}% validates the adaptive 
            approach for practical QKD deployment under dynamic channel conditions.
            """)


def run_key_rate_analysis_mode(num_qubits):
    """Dedicated key rate analysis mode."""
    
    st.sidebar.header("🔬 Key Rate Analysis")
    
    eve_probs = st.sidebar.multiselect(
        "Eve Probabilities to Test",
        [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        default=[0.0, 0.2, 0.4, 0.6, 0.8]
    )
    
    trials = st.sidebar.slider("Trials per Probability", 1, 20, 10, 1)
    
    # Key rate parameters
    st.sidebar.subheader("⚙️ Key Rate Parameters")
    mu = st.sidebar.slider("Mean Photon Number (μ)", 0.1, 1.0, 0.5, 0.1,
                           help="Average number of photons per signal pulse")
    f = st.sidebar.slider("Error Correction Efficiency (f)", 1.0, 1.5, 1.16, 0.01,
                          help="Shannon limit ≈ 1.0, practical ≈ 1.16")
    
    run_button = st.sidebar.button("🚀 Analyze Key Rates", type="primary")
    
    if run_button and eve_probs:
        with st.spinner("Computing secret key rates..."):
            results = run_eve_sweep_with_key_rate(
                num_qubits=num_qubits,
                eve_probs=sorted(eve_probs),
                trials=trials,
                mu=mu,
                f=f
            )
            st.session_state.key_rate_results = results
    
    if 'key_rate_results' in st.session_state:
        results = st.session_state.key_rate_results
        
        st.header("📊 Secret Key Rate Analysis")
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        import pandas as pd
        summary_data = []
        for r in results:
            summary_data.append({
                'Eve Probability': r['eve_probability'],
                'Mean QBER (%)': r['mean_qber'] * 100,
                'Mean Key Length': r['mean_key_length'],
                'Mean Key Rate': r['mean_key_rate'],
                'Std Key Rate': r['std_key_rate'],
                'Positive Rate %': r['key_rate_stats']['positive_rate_fraction'] * 100
            })
        df = pd.DataFrame(summary_data)
        st.dataframe(df.round(6), use_container_width=True)
        
        # Key metrics
        st.subheader("🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            max_rate_idx = df['Mean Key Rate'].idxmax()
            max_rate = df.loc[max_rate_idx, 'Mean Key Rate']
            max_rate_eve = df.loc[max_rate_idx, 'Eve Probability']
            st.metric("Max Key Rate", f"{max_rate:.6f}", 
                     f"at Eve = {max_rate_eve:.1f}")
        
        with col2:
            zero_rate_threshold = df[df['Mean Key Rate'] <= 0]['Eve Probability'].min()
            if pd.notna(zero_rate_threshold):
                st.metric("Key Rate → 0", f"Eve ≥ {zero_rate_threshold:.1f}")
            else:
                st.metric("Key Rate → 0", "N/A")
        
        with col3:
            avg_qber = df['Mean QBER (%)'].mean()
            st.metric("Average QBER", f"{avg_qber:.2f}%")
        
        with col4:
            total_positive = df['Positive Rate %'].mean()
            st.metric("Avg Positive Rate", f"{total_positive:.1f}%")
        
        # Visualizations
        st.header("📊 Key Rate Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Key Rate vs Eve Probability")
            fig_rate_eve = plot_key_rate_vs_eve(results)
            st.pyplot(fig_rate_eve)
        
        with col2:
            st.subheader("Key Rate vs QBER")
            fig_rate_qber = plot_key_rate_vs_qber(results)
            st.pyplot(fig_rate_qber)
        
        # Download results
        st.subheader("💾 Export Results")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="key_rate_analysis.csv",
            mime="text/csv"
        )


def run_pns_attack_mode(num_qubits):
    """Photon Number Splitting attack analysis mode."""
    
    st.sidebar.header("🔬 PNS Attack Parameters")
    
    mu_signal = st.sidebar.slider(
        "Signal Mean Photon Number (μ)",
        0.1, 1.5, 0.5, 0.1,
        help="Higher μ = more multi-photon pulses"
    )
    
    mu_decoy = st.sidebar.slider(
        "Decoy Mean Photon Number",
        0.01, 0.3, 0.1, 0.01
    )
    
    channel_loss = st.sidebar.slider(
        "Channel Loss",
        0.0, 0.5, 0.1, 0.05
    )
    
    detector_efficiency = st.sidebar.slider(
        "Detector Efficiency",
        0.1, 1.0, 0.5, 0.1
    )
    
    # Analysis type
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Single Run", "Parameter Sweep", "Attack Comparison"]
    )
    
    if analysis_type == "Single Run":
        run_button = st.sidebar.button("🚀 Run PNS Attack", type="primary")
        
        if run_button:
            with st.spinner("Running PNS attack simulation..."):
                from bb84.pns_attack import run_bb84_with_pns_attack
                result = run_bb84_with_pns_attack(
                    num_pulses=num_qubits,
                    mu_signal=mu_signal,
                    mu_decoy=mu_decoy,
                    channel_loss=channel_loss,
                    detector_efficiency=detector_efficiency
                )
                st.session_state.pns_result = result
        
        if 'pns_result' in st.session_state:
            result = st.session_state.pns_result
            
            st.header("📊 PNS Attack Results")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("QBER", f"{result['qber']*100:.2f}%")
            with col2:
                st.metric("Key Length", result['key_length'])
            with col3:
                eve_info = result['eve_results']['information_gain'] * 100
                st.metric("Eve's Info Gain", f"{eve_info:.2f}%")
            with col4:
                multi_photon = result['attack_stats']['multi_photon_fraction'] * 100
                st.metric("Multi-Photon %", f"{multi_photon:.2f}%")
            
            # Detection rates
            st.header("🎯 Detection Rate Analysis")
            det_stats = result['detection_stats']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Signal Detection Rate", 
                         f"{det_stats['signal_detection_rate']:.4f}")
            with col2:
                st.metric("Decoy Detection Rate",
                         f"{det_stats['decoy_detection_rate']:.4f}")
            with col3:
                st.metric("Vacuum Detection Rate",
                         f"{det_stats['vacuum_detection_rate']:.4f}")
            
            # Attack statistics
            with st.expander("📋 Detailed Attack Statistics"):
                import pandas as pd
                attack_stats = result['attack_stats']
                stats_df = pd.DataFrame([{
                    'Total Pulses': attack_stats['total_pulses'],
                    'Vacuum Pulses': attack_stats['vacuum_pulses'],
                    'Single-Photon Pulses': attack_stats['single_photon_pulses'],
                    'Multi-Photon Pulses': attack_stats['multi_photon_pulses'],
                    'Eve Stored': attack_stats['eve_stored_photons'],
                    'Eve Measured': attack_stats['eve_successful_measurements'],
                    'Storage Success Rate': f"{attack_stats['storage_success_rate']:.3f}"
                }])
                st.dataframe(stats_df.T, use_container_width=True)
    
    elif analysis_type == "Parameter Sweep":
        mu_values = st.sidebar.multiselect(
            "Mean Photon Numbers to Test",
            [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5],
            default=[0.2, 0.5, 1.0]
        )
        
        trials = st.sidebar.slider("Trials per Value", 1, 20, 5)
        
        run_button = st.sidebar.button("🚀 Run Sweep", type="primary")
        
        if run_button and mu_values:
            with st.spinner("Running parameter sweep..."):
                from bb84.pns_experiments import run_pns_parameter_sweep
                results = run_pns_parameter_sweep(
                    num_pulses=num_qubits,
                    mu_signal_values=mu_values,
                    trials=trials
                )
                st.session_state.pns_sweep_results = results
        
        if 'pns_sweep_results' in st.session_state:
            results = st.session_state.pns_sweep_results
            
            st.header("📊 PNS Parameter Sweep Results")
            
            # Summary table
            import pandas as pd
            summary_data = []
            for r in results:
                summary_data.append({
                    'μ (signal)': r['mu_signal'],
                    'Mean QBER (%)': r['mean_qber'] * 100,
                    'Mean Key Rate': r['mean_key_rate'],
                    'Eve Info Gain (%)': r['mean_eve_info_gain'] * 100,
                    'Signal Det. Rate': r['mean_signal_detection_rate'],
                    'Decoy Det. Rate': r['mean_decoy_detection_rate']
                })
            df = pd.DataFrame(summary_data)
            st.dataframe(df.round(4), use_container_width=True)
            
            # Plots
            st.header("📈 Analysis Plots")
            
            col1, col2 = st.columns(2)
            with col1:
                fig1 = plot_detection_rates_signal_vs_decoy(results)
                st.pyplot(fig1)
            
            with col2:
                fig2 = plot_qber_under_pns(results)
                st.pyplot(fig2)
            
            col1, col2 = st.columns(2)
            with col1:
                fig3 = plot_key_rate_under_pns(results)
                st.pyplot(fig3)
            
            with col2:
                fig4 = plot_eve_information_gain_pns(results)
                st.pyplot(fig4)
    
    elif analysis_type == "Attack Comparison":
        eve_prob = st.sidebar.slider(
            "Eve Probability (for IR attack)",
            0.0, 1.0, 0.5, 0.1
        )
        
        trials = st.sidebar.slider("Trials", 1, 20, 10)
        
        run_button = st.sidebar.button("🚀 Compare Attacks", type="primary")
        
        if run_button:
            with st.spinner("Comparing attacks..."):
                from bb84.pns_experiments import compare_intercept_resend_vs_pns
                comparison = compare_intercept_resend_vs_pns(
                    num_pulses=num_qubits,
                    eve_probability=eve_prob,
                    mu_signal=mu_signal,
                    trials=trials
                )
                st.session_state.attack_comparison = comparison
        
        if 'attack_comparison' in st.session_state:
            comp = st.session_state.attack_comparison
            
            st.header("⚔️ Attack Comparison: IR vs PNS")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Intercept-Resend")
                st.metric("QBER", f"{comp['intercept_resend']['mean_qber']*100:.2f}%")
                st.metric("Key Rate", f"{comp['intercept_resend']['mean_key_rate']:.6f}")
            
            with col2:
                st.subheader("PNS Attack")
                st.metric("QBER", f"{comp['pns_attack']['mean_qber']*100:.2f}%")
                st.metric("Key Rate", f"{comp['pns_attack']['mean_key_rate']:.6f}")
                st.metric("Eve Info Gain", f"{comp['pns_attack']['mean_eve_info_gain']*100:.2f}%")
            
            st.header("📊 Comparison Plot")
            fig = plot_attack_comparison_ir_vs_pns(comp)
            st.pyplot(fig)
            
            with st.expander("📝 Analysis"):
                st.markdown(f"""
                ### Key Findings
                
                **QBER:**
                - Intercept-Resend: {comp['intercept_resend']['mean_qber']*100:.2f}%
                - PNS: {comp['pns_attack']['mean_qber']*100:.2f}%
                - Difference: {comp['comparison']['qber_difference']*100:.2f}%
                
                **Key Rate:**
                - Intercept-Resend: {comp['intercept_resend']['mean_key_rate']:.6f} bits/pulse
                - PNS: {comp['pns_attack']['mean_key_rate']:.6f} bits/pulse
                - Difference: {comp['comparison']['key_rate_difference']:.6f} bits/pulse
                
                **Conclusion:**
                PNS attack is {'more stealthy' if comp['comparison']['pns_advantage'] == 'PNS' else 'less stealthy'} 
                than Intercept-Resend, with {'lower' if comp['comparison']['pns_advantage'] == 'PNS' else 'higher'} QBER.
                
                This demonstrates why decoy-state protocols are essential for detecting PNS attacks.
                """)


def run_distance_analysis_mode(num_qubits, eve_probability):
    """Distance-dependent QKD analysis mode."""
    
    st.sidebar.header("📡 Distance Analysis Parameters")
    
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Distance Sweep", "Strategy vs Distance"]
    )
    
    # Common parameters
    fiber_loss = st.sidebar.slider(
        "Fiber Loss (dB/km)",
        0.1, 0.5, 0.2, 0.05,
        help="Typical: 0.2 dB/km @ 1550nm"
    )
    
    detector_eff = st.sidebar.slider(
        "Detector Efficiency",
        0.1, 1.0, 0.5, 0.1
    )
    
    dark_count_rate = st.sidebar.slider(
        "Dark Count Rate",
        1e-7, 1e-5, 1e-6, 1e-7,
        format="%.1e",
        help="Dark counts per detection gate"
    )
    
    if analysis_type == "Distance Sweep":
        # Distance selection
        distance_option = st.sidebar.radio(
            "Distance Selection",
            ["Preset Range", "Custom Range"]
        )
        
        if distance_option == "Preset Range":
            preset = st.sidebar.selectbox(
                "Preset",
                ["Short (10-50 km)", "Medium (20-100 km)", "Long (50-150 km)"]
            )
            
            if preset == "Short (10-50 km)":
                distances = [10, 20, 30, 40, 50]
            elif preset == "Medium (20-100 km)":
                distances = [20, 40, 60, 80, 100]
            else:
                distances = [50, 75, 100, 125, 150]
        else:
            min_dist = st.sidebar.number_input("Min Distance (km)", 5, 200, 10)
            max_dist = st.sidebar.number_input("Max Distance (km)", min_dist+5, 300, 100)
            num_points = st.sidebar.slider("Number of Points", 3, 15, 7)
            distances = np.linspace(min_dist, max_dist, num_points).tolist()
        
        trials = st.sidebar.slider("Trials per Distance", 1, 10, 5)
        
        run_button = st.sidebar.button("🚀 Run Distance Sweep", type="primary")
        
        if run_button:
            with st.spinner("Running distance sweep..."):
                from bb84.distance_experiments import run_distance_sweep
                results = run_distance_sweep(
                    distances_km=distances,
                    num_qubits=num_qubits,
                    eve_probability=eve_probability,
                    dark_count_rate=dark_count_rate,
                    trials=trials
                )
                st.session_state.distance_results = results
        
        if 'distance_results' in st.session_state:
            results = st.session_state.distance_results
            
            st.header("📊 Distance-Dependent QKD Analysis")
            
            # Summary table
            import pandas as pd
            summary_data = []
            for r in results:
                summary_data.append({
                    'Distance (km)': r['distance_km'],
                    'Transmittance (η)': r['transmittance'],
                    'Mean QBER (%)': r['mean_qber'] * 100,
                    'Mean Key Rate': r['mean_key_rate'],
                    'Mean Detections': r['mean_detections']
                })
            df = pd.DataFrame(summary_data)
            st.dataframe(df.round(6), use_container_width=True)
            
            # Key metrics
            st.subheader("🎯 Key Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_distance = max([r['distance_km'] for r in results if r['mean_key_rate'] > 0], default=0)
                st.metric("Max Viable Distance", f"{max_distance:.0f} km",
                         help="Maximum distance with positive key rate")
            
            with col2:
                min_qber = min([r['mean_qber'] for r in results])
                st.metric("Min QBER", f"{min_qber*100:.2f}%")
            
            with col3:
                max_key_rate = max([r['mean_key_rate'] for r in results])
                st.metric("Max Key Rate", f"{max_key_rate:.6f} bits/pulse")
            
            # Visualizations
            st.header("📈 Distance Analysis Plots")
            fig = plot_key_rate_vs_distance(results)
            st.pyplot(fig)
            
            # Research interpretation
            with st.expander("📝 Research Interpretation"):
                st.markdown(f"""
                ### Distance-Dependent Analysis
                
                **Channel Model:**
                - Fiber loss: {fiber_loss} dB/km
                - Detector efficiency: {detector_eff}
                - Dark count rate: {dark_count_rate:.1e}
                
                **Key Observations:**
                1. **Maximum viable distance:** {max_distance} km
                   - Beyond this distance, key rate drops to zero
                   - Limitation due to channel loss and detector noise
                
                2. **Loss scaling:** η(L) = 10^(-{fiber_loss}·L/10)
                   - At {distances[0]} km: η = {results[0]['transmittance']:.4f}
                   - At {distances[-1]} km: η = {results[-1]['transmittance']:.6f}
                
                3. **QBER behavior:**
                   - Increases with distance due to dark counts
                   - Dark counts become dominant at long distances
                
                **Practical Implications:**
                - Short-distance QKD (< 50 km): High key rates, suitable for metro networks
                - Medium-distance (50-100 km): Moderate key rates, requires optimization
                - Long-distance (> 100 km): Very low rates, may need quantum repeaters
                """)
            
            # Download results
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Distance Analysis CSV",
                data=csv,
                file_name="distance_analysis.csv",
                mime="text/csv"
            )
    
    elif analysis_type == "Strategy vs Distance":
        # Distance range
        distances = st.sidebar.multiselect(
            "Distances to Test (km)",
            [10, 25, 50, 75, 100, 125, 150],
            default=[25, 50, 75, 100]
        )
        
        strategies = st.sidebar.multiselect(
            "Strategies to Compare",
            ["qber_based", "multi_metric", "attack_aware", "hybrid"],
            default=["qber_based", "multi_metric"]
        )
        
        num_rounds = st.sidebar.slider("Rounds per Experiment", 5, 30, 15, 5)
        trials = st.sidebar.slider("Trials", 1, 5, 2)
        
        run_button = st.sidebar.button("🚀 Compare Strategies vs Distance", type="primary")
        
        if run_button and distances and strategies:
            with st.spinner("Comparing strategies across distances..."):
                from bb84.distance_experiments import compare_strategies_vs_distance
                comparison = compare_strategies_vs_distance(
                    distances_km=sorted(distances),
                    strategies=strategies,
                    num_rounds=num_rounds,
                    qubits_per_round=num_qubits,
                    eve_probability=eve_probability,
                    trials=trials
                )
                st.session_state.strategy_distance_comparison = comparison
        
        if 'strategy_distance_comparison' in st.session_state:
            comparison = st.session_state.strategy_distance_comparison
            
            st.header("🏆 Strategy Performance vs Distance")
            
            # Plot comparison
            #fig = plot_strategies_vs_distance(comparison)
            st.pyplot(fig)
            
            # Detailed results table
            with st.expander("📋 Detailed Results"):
                import pandas as pd
                for strategy, results in comparison.items():
                    st.subheader(f"Strategy: {strategy}")
                    df = pd.DataFrame(results)
                    st.dataframe(df.round(6), use_container_width=True)
            
            # Analysis
            with st.expander("📝 Comparative Analysis"):
                st.markdown("""
                ### Strategy Comparison Across Distance
                
                **Key Questions:**
                1. Which strategy maintains highest key rate at long distances?
                2. How does QBER scale differently for each strategy?
                3. At what distance do strategies converge in performance?
                
                **Observations:**
                - All strategies degrade with distance due to channel loss
                - Adaptive strategies may maintain better performance at medium distances
                - Dark counts dominate QBER at very long distances, limiting all strategies
                
                **Recommendation:**
                - For short distances (< 50 km): Use strategy optimized for throughput
                - For medium distances (50-100 km): Adaptive strategies show advantage
                - For long distances (> 100 km): Channel loss dominates; consider repeaters
                """)


def run_chaotic_rng_mode(num_qubits):
    """Chaotic Random Number Generator analysis mode."""
    
    st.sidebar.header("🌀 Chaotic RNG Parameters")
    
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["RNG Characterization", "Pulse Selection Comparison", "Randomness Testing"]
    )
    
    # RNG selection
    rng_type = st.sidebar.selectbox(
        "Chaotic System",
        ["Logistic Map", "Lorenz System", "Henon Map"],
        help="Select chaotic system for random number generation"
    )
    
    if analysis_type == "RNG Characterization":
        n_samples = st.sidebar.slider("Number of Samples", 1000, 50000, 10000, 1000)
        
        # System-specific parameters
        if rng_type == "Logistic Map":
            r_param = st.sidebar.slider("r parameter", 3.57, 4.0, 3.99, 0.01,
                                       help="Control parameter (chaotic for r > 3.57)")
            seed = st.sidebar.slider("Seed", 0.01, 0.99, 0.5, 0.01)
            rng_params = {'r': r_param, 'seed': seed}
        
        elif rng_type == "Lorenz System":
            sigma = st.sidebar.slider("σ (sigma)", 5.0, 20.0, 10.0, 1.0)
            rho = st.sidebar.slider("ρ (rho)", 20.0, 35.0, 28.0, 1.0)
            beta = st.sidebar.slider("β (beta)", 1.0, 4.0, 8/3, 0.1)
            rng_params = {'sigma': sigma, 'rho': rho, 'beta': beta}
        
        else:  # Henon Map
            a_param = st.sidebar.slider("a parameter", 1.0, 1.8, 1.4, 0.1)
            b_param = st.sidebar.slider("b parameter", 0.1, 0.5, 0.3, 0.05)
            rng_params = {'a': a_param, 'b': b_param}
        
        run_button = st.sidebar.button("🚀 Characterize RNG", type="primary")
        
        if run_button:
            with st.spinner("Generating and analyzing chaotic sequence..."):
                from bb84.chaotic_rng import LogisticMap, LorenzSystem, HenonMap
                
                # Create RNG
                if rng_type == "Logistic Map":
                    rng = LogisticMap(**rng_params)
                elif rng_type == "Lorenz System":
                    rng = LorenzSystem(**rng_params)
                else:
                    rng = HenonMap(**rng_params)
                
                # Generate sequence
                sequence = rng.generate(n_samples)
                
                st.session_state.chaotic_sequence = sequence
                st.session_state.chaotic_rng = rng
        
        if 'chaotic_sequence' in st.session_state:
            sequence = st.session_state.chaotic_sequence
            rng = st.session_state.chaotic_rng
            
            st.header(f"📊 {rng_type} Characterization")
            
            # Statistical properties
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{np.mean(sequence):.4f}")
            with col2:
                st.metric("Std Dev", f"{np.std(sequence):.4f}")
            with col3:
                st.metric("Min", f"{np.min(sequence):.4f}")
            with col4:
                st.metric("Max", f"{np.max(sequence):.4f}")
            
            # Visualization
            st.header("📈 Chaotic Sequence Analysis")
            fig = plot_chaotic_sequence(rng, n=min(n_samples, 5000))
            st.pyplot(fig)
            
            # Interpretation
            with st.expander("📝 Chaotic System Properties"):
                if rng_type == "Logistic Map":
                    st.markdown(f"""
                    ### Logistic Map: x_{{n+1}} = r·x_n·(1 - x_n)
                    
                    **Parameters:**
                    - r = {rng_params['r']} (chaotic for r > 3.57)
                    - Seed = {rng_params['seed']}
                    
                    **Characteristics:**
                    - Simple 1D map with complex behavior
                    - Fully chaotic at r = 4.0
                    - Fast generation, low memory
                    
                    **Advantages:**
                    - Computationally efficient
                    - Well-studied dynamical system
                    - Good for high-speed applications
                    """)
                
                elif rng_type == "Lorenz System":
                    st.markdown(f"""
                    ### Lorenz System (Weather Model)
                    
                    **Parameters:**
                    - σ = {rng_params['sigma']}
                    - ρ = {rng_params['rho']}
                    - β = {rng_params['beta']:.2f}
                    
                    **Characteristics:**
                    - 3D continuous-time system
                    - Strange attractor (butterfly shape)
                    - Highly sensitive to initial conditions
                    
                    **Advantages:**
                    - Very complex dynamics
                    - Multiple independent sequences (x, y, z)
                    - Difficult to predict
                    """)
                
                else:
                    st.markdown(f"""
                    ### Henon Map
                    
                    **Parameters:**
                    - a = {rng_params['a']}
                    - b = {rng_params['b']}
                    
                    **Characteristics:**
                    - 2D discrete map
                    - Strange attractor
                    - Mixing and ergodic
                    
                    **Advantages:**
                    - Balance between complexity and speed
                    - 2D phase space
                    - Good statistical properties
                    """)
    
    elif analysis_type == "Pulse Selection Comparison":
        n_pulses = st.sidebar.slider("Number of Pulses", 1000, 20000, 5000, 1000)
        
        # Target probabilities
        with st.sidebar.expander("Target Probabilities"):
            signal_prob = st.slider("Signal", 0.4, 0.85, 0.70, 0.05)
            decoy_prob = st.slider("Decoy", 0.1, 0.5, 0.20, 0.05)
            vacuum_prob = 1.0 - signal_prob - decoy_prob
            st.metric("Vacuum (auto)", f"{vacuum_prob:.2f}")
        
        run_button = st.sidebar.button("🚀 Compare Pulse Selection", type="primary")
        
        if run_button:
            with st.spinner("Comparing standard vs chaotic pulse selection..."):
                from bb84.chaotic_rng import ChaoticPulseSelector
                
                # Standard PRNG
                standard_types = np.random.choice(
                    [0, 1, 2],
                    size=n_pulses,
                    p=[signal_prob, decoy_prob, vacuum_prob]
                )
                
                # Chaotic RNG
                if rng_type == "Logistic Map":
                    chaotic_selector = ChaoticPulseSelector(
                        rng_type='logistic',
                        signal_prob=signal_prob,
                        decoy_prob=decoy_prob,
                        vacuum_prob=vacuum_prob
                    )
                elif rng_type == "Lorenz System":
                    chaotic_selector = ChaoticPulseSelector(
                        rng_type='lorenz',
                        signal_prob=signal_prob,
                        decoy_prob=decoy_prob,
                        vacuum_prob=vacuum_prob
                    )
                else:
                    chaotic_selector = ChaoticPulseSelector(
                        rng_type='henon',
                        signal_prob=signal_prob,
                        decoy_prob=decoy_prob,
                        vacuum_prob=vacuum_prob
                    )
                
                chaotic_types = chaotic_selector.generate_pulse_types(n_pulses)
                
                # Get actual probabilities
                standard_probs = chaotic_selector.get_actual_probabilities(standard_types)
                chaotic_probs = chaotic_selector.get_actual_probabilities(chaotic_types)
                
                st.session_state.pulse_comparison = {
                    'standard_types': standard_types,
                    'chaotic_types': chaotic_types,
                    'standard_probs': standard_probs,
                    'chaotic_probs': chaotic_probs,
                    'target_probs': {
                        'signal': signal_prob,
                        'decoy': decoy_prob,
                        'vacuum': vacuum_prob
                    }
                }
        
        if 'pulse_comparison' in st.session_state:
            comp = st.session_state.pulse_comparison
            
            st.header("📊 Pulse Selection Comparison")
            
            # Probability comparison table
            import pandas as pd
            prob_data = []
            
            prob_data.append({
                'Method': 'Target',
                'Signal': comp['target_probs']['signal'],
                'Decoy': comp['target_probs']['decoy'],
                'Vacuum': comp['target_probs']['vacuum']
            })
            
            prob_data.append({
                'Method': 'Standard PRNG',
                'Signal': comp['standard_probs']['signal'],
                'Decoy': comp['standard_probs']['decoy'],
                'Vacuum': comp['standard_probs']['vacuum']
            })
            
            prob_data.append({
                'Method': f'Chaotic ({rng_type})',
                'Signal': comp['chaotic_probs']['signal'],
                'Decoy': comp['chaotic_probs']['decoy'],
                'Vacuum': comp['chaotic_probs']['vacuum']
            })
            
            df = pd.DataFrame(prob_data)
            st.dataframe(df.round(4), use_container_width=True)
            
            # Deviation from target
            st.subheader("📉 Deviation from Target Probabilities")
            
            standard_dev = {
                'signal': abs(comp['standard_probs']['signal'] - comp['target_probs']['signal']),
                'decoy': abs(comp['standard_probs']['decoy'] - comp['target_probs']['decoy']),
                'vacuum': abs(comp['standard_probs']['vacuum'] - comp['target_probs']['vacuum'])
            }
            
            chaotic_dev = {
                'signal': abs(comp['chaotic_probs']['signal'] - comp['target_probs']['signal']),
                'decoy': abs(comp['chaotic_probs']['decoy'] - comp['target_probs']['decoy']),
                'vacuum': abs(comp['chaotic_probs']['vacuum'] - comp['target_probs']['vacuum'])
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Standard PRNG Total Deviation", 
                         f"{sum(standard_dev.values()):.4f}")
            with col2:
                st.metric("Chaotic RNG Total Deviation",
                         f"{sum(chaotic_dev.values()):.4f}")
            
            # Visualization
            st.header("📈 Distribution Comparison")
            fig = plot_pulse_distribution_comparison(
                comp['standard_types'],
                comp['chaotic_types']
            )
            st.pyplot(fig)
            
            # Analysis
            with st.expander("📝 Analysis & Research Implications"):
                st.markdown(f"""
                ### Pulse Selection Analysis
                
                **Target Distribution:**
                - Signal: {comp['target_probs']['signal']:.3f}
                - Decoy: {comp['target_probs']['decoy']:.3f}
                - Vacuum: {comp['target_probs']['vacuum']:.3f}
                
                **Standard PRNG Performance:**
                - Total deviation: {sum(standard_dev.values()):.4f}
                - Uses NumPy's Mersenne Twister (MT19937)
                - Predictable period: 2^19937 - 1
                
                **Chaotic RNG Performance:**
                - Total deviation: {sum(chaotic_dev.values()):.4f}
                - System: {rng_type}
                - Non-periodic, continuous spectrum
                
                **Key Advantage of Chaotic RNG:**
                1. **Unpredictability**: No deterministic period
                2. **Side-channel resistance**: Harder to predict from partial information
                3. **Security**: Eve cannot predict pulse types even with timing info
                
                **Research Contribution:**
                - Chaotic RNG provides stronger security against side-channel attacks
                - Maintains target distribution while adding chaos-based unpredictability
                - Novel application to decoy-state QKD
                """)
    
    elif analysis_type == "Randomness Testing":
        n_samples = st.sidebar.slider("Samples for Testing", 5000, 100000, 10000, 5000)
        
        run_button = st.sidebar.button("🚀 Run Randomness Tests", type="primary")
        
        if run_button:
            with st.spinner("Running comprehensive randomness tests..."):
                from bb84.chaotic_rng import (
                    LogisticMap, LorenzSystem, HenonMap,
                    comprehensive_randomness_test
                )
                
                # Create RNG
                if rng_type == "Logistic Map":
                    rng = LogisticMap()
                elif rng_type == "Lorenz System":
                    rng = LorenzSystem()
                else:
                    rng = HenonMap()
                
                # Run comprehensive tests
                test_results = comprehensive_randomness_test(rng, n=n_samples)
                
                st.session_state.randomness_tests = test_results
        
        if 'randomness_tests' in st.session_state:
            results = st.session_state.randomness_tests
            
            st.header("🧪 Randomness Test Results")
            
            # Overall result
            if results['overall_passed']:
                st.success("✅ **PASSED**: Sequence passes randomness tests")
            else:
                st.error("❌ **FAILED**: Sequence fails one or more tests")
            
            # Statistical properties
            st.subheader("📊 Statistical Properties")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mean", f"{results['mean']:.4f}",
                         help="Should be close to 0.5 for uniform distribution")
            with col2:
                st.metric("Std Dev", f"{results['std']:.4f}",
                         help="Should be close to 0.289 for uniform [0,1]")
            
            # Chi-square test
            st.subheader("📈 Chi-Square Uniformity Test")
            chi_result = results['chi_square_test']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("χ² Statistic", f"{chi_result['chi_square']:.2f}")
            with col2:
                st.metric("Critical Value", f"{chi_result['critical_value']:.2f}")
            with col3:
                if chi_result['passed']:
                    st.success("✅ PASSED")
                else:
                    st.error("❌ FAILED")
            
            # Runs test
            st.subheader("🏃 Runs Test (Independence)")
            runs_result = results['runs_test']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Observed Runs", runs_result['runs'])
            with col2:
                st.metric("Expected Runs", f"{runs_result['expected_runs']:.1f}")
            with col3:
                if runs_result['passed']:
                    st.success("✅ PASSED")
                else:
                    st.error("❌ FAILED")
            
            st.metric("Z-Score", f"{runs_result['z_score']:.3f}",
                     help="|z| < 1.96 indicates independence at 95% confidence")
            
            # Interpretation
            with st.expander("📝 Test Interpretation"):
                st.markdown("""
                ### NIST-Style Randomness Testing
                
                **Chi-Square Test:**
                - Tests uniformity of distribution
                - Bins the data and compares to expected uniform distribution
                - PASS: χ² < critical value (16.919 for 9 degrees of freedom)
                
                **Runs Test:**
                - Tests independence between consecutive values
                - Counts sequences above/below median
                - PASS: |z-score| < 1.96 at 95% confidence
                
                **For QKD Applications:**
                - Both tests must pass for secure pulse selection
                - Chi-square ensures unbiased pulse type distribution
                - Runs test ensures Eve cannot predict next pulse from previous
                
                **Advantages of Chaotic RNG:**
                1. Passes standard randomness tests
                2. No periodic structure (unlike PRNGs)
                3. Difficult to reverse-engineer from partial sequence
                4. Suitable for cryptographic applications
                """)
            
            # Download results
            import pandas as pd
            test_summary = pd.DataFrame([{
                'RNG Type': results['rng_type'],
                'Samples': results['n_samples'],
                'Mean': results['mean'],
                'Std Dev': results['std'],
                'Chi-Square': chi_result['chi_square'],
                'Chi-Square Passed': chi_result['passed'],
                'Runs': runs_result['runs'],
                'Z-Score': runs_result['z_score'],
                'Runs Passed': runs_result['passed'],
                'Overall Passed': results['overall_passed']
            }])
            
            csv = test_summary.to_csv(index=False)
            st.download_button(
                label="📥 Download Test Results CSV",
                data=csv,
                file_name=f"randomness_test_{rng_type.replace(' ', '_')}.csv",
                mime="text/csv"
            )

def run_research_evaluation_mode(num_qubits: int):
    """Journal-level research evaluation mode (fixed integration)."""
    import streamlit as st
    from bb84.research_evaluation import ComprehensiveExperiment
 
    st.header("📊 Research Evaluation (Journal Level)")
    st.markdown(
        "Evaluates four dimensions: QBER stability, attack detection, "
        "key generation rate, and adaptability to channel changes."
    )
 
    # ── Sidebar controls ────────────────────────────────────────────
    st.sidebar.header("🔬 Research Parameters")
    num_trials  = st.sidebar.slider("Number of Trials",    5,  50, 10)
    num_rounds  = st.sidebar.slider("Rounds per Trial",   20, 100, 50)
    eve_prob    = st.sidebar.slider("Eve Probability",    0.0, 1.0, 0.3)
 
    run_button = st.sidebar.button("🚀 Run Research Evaluation", type="primary")
 
    if not run_button:
        st.info("Configure parameters in the sidebar, then click **Run Research Evaluation**.")
        return
 
    experiment = ComprehensiveExperiment(num_trials=num_trials, seed=42)
 
    # ── (A) QBER Stability ──────────────────────────────────────────
    st.subheader("🔐 (A) QBER Stability")
    with st.spinner("Running QBER stability experiment…"):
        results_a = experiment.run_experiment_a_qber_stability(
            num_rounds=num_rounds,
            qubits_per_round=num_qubits,
            eve_probability=eve_prob,
        )
    if results_a:
        fig1 = plot_qber_stability(results_a)
        st.pyplot(fig1)
        plt.close(fig1)
    else:
        st.warning("No QBER stability data returned.")
 
    # ── (B) Attack Detection ────────────────────────────────────────
    st.subheader("🚨 (B) Attack Detection Capability")
    with st.spinner("Running attack detection experiment…"):
        results_b = experiment.run_experiment_b_attack_detection(
            num_rounds=num_rounds,
            qubits_per_round=num_qubits,
            # eve_probabilities defaults to [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        )
    if results_b:
        fig2 = plot_attack_detection(results_b)
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.warning("No attack detection data returned.")
 
    # ── (C) Key Generation Rate ─────────────────────────────────────
    st.subheader("📉 (C) Key Rate Under Attack")
    with st.spinner("Running key generation experiment…"):
        results_c = experiment.run_experiment_c_key_generation(
            num_rounds=num_rounds,
            qubits_per_round=num_qubits,
            # eve_probabilities defaults to [0.0, 0.2, 0.4, 0.6, 0.8]
        )
    if results_c:
        fig3 = plot_key_rate(results_c)
        st.pyplot(fig3)
        plt.close(fig3)
    else:
        st.warning("No key generation data returned.")
 
    # ── (D) Adaptability ────────────────────────────────────────────
    st.subheader("🔄 (D) Adaptability to Channel Changes")
    with st.spinner("Running adaptability experiment…"):
        results_d = experiment.run_experiment_d_adaptability(
            num_rounds=100,
            qubits_per_round=num_qubits,
            # change_points defaults to [25, 50, 75]
        )
    if results_d:
        fig4 = plot_adaptability(results_d)
        st.pyplot(fig4)
        plt.close(fig4)
    else:
        st.warning("No adaptability data returned.")
 
    st.success("✅ Research Evaluation Completed!")
 

if __name__ == "__main__":
    main()