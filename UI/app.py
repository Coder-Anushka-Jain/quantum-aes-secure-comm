"""
Streamlit Application for BB84 + AES Secure Communication System

Extended with Adaptive Decoy-State QKD capabilities and Secret Key Rate Analysis.
"""

import streamlit as st
import numpy as np
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

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
    plot_adaptive_key_rate_evolution, plot_static_vs_adaptive_key_rate
)
from bb84.key_rate_calculator import compute_key_rate_from_result
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib


# Page configuration
st.set_page_config(
    page_title="Adaptive BB84 Quantum-Classical Secure Communication",
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
    st.title("🔐 Adaptive BB84 Quantum-Classical Secure Communication")
    st.markdown("""
    ### Advanced Hybrid Quantum–Classical Cryptography with Adaptive Decoy States
    **Research Features:** Dynamic decoy probability optimization, multi-strategy comparison, 
    secret key rate analysis, and real-time attack mitigation.
    """)
    
    st.divider()
    
    # Sidebar - Mode Selection
    st.sidebar.header("🎛️ Mode Selection")
    
    mode = st.sidebar.radio(
        "Operation Mode",
        ["Single Run", "Adaptive Multi-Round", "Strategy Comparison", 
         "Static vs Adaptive", "Key Rate Analysis"],
        help="Choose experiment type"
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
        
        # Display results (original UI code)
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
        
        # Interpretation
        with st.expander("📝 Interpretation Guide"):
            st.markdown(f"""
            ### Understanding the Results
            
            **Key Rate Formula:**
```
            R = Q₁(1 - H(e₁)) - Qμ·f·H(Eμ)
```
            
            **Parameter Settings:**
            - Mean photon number (μ): {mu}
            - Error correction efficiency (f): {f}
            - Qubits per round: {num_qubits}
            
            **Key Observations:**
            1. **Positive key rate** (R > 0): Secure key distribution is possible
            2. **Zero/Negative key rate** (R ≤ 0): Eve's presence makes secure communication impossible
            3. **Theoretical threshold**: Key rate typically drops to zero when QBER > 11%
            
            **Your Results:**
            - Maximum key rate: {max_rate:.6f} bits/pulse at Eve probability = {max_rate_eve:.1f}
            - Average QBER across all trials: {avg_qber:.2f}%
            - The key rate decreases with increasing Eve probability due to higher QBER
            
            **Research Implications:**
            - Compare these results with theoretical predictions
            - Analyze the relationship between QBER and key rate
            - Consider adaptive strategies to maintain higher key rates under attack
            """)
        
        # Download results
        st.subheader("💾 Export Results")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="key_rate_analysis.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()