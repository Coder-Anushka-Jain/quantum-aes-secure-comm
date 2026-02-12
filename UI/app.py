"""
Streamlit Application for BB84 + AES Secure Communication System

Extended with Adaptive Decoy-State QKD capabilities.
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
    compare_adaptive_strategies, run_static_vs_adaptive_comparison
)
from bb84.plot_results import (
    plot_qber, plot_qber_vs_eve, plot_key_length_vs_eve,
    plot_adaptive_qber_evolution, plot_decoy_probability_evolution,
    plot_strategy_comparison, plot_static_vs_adaptive
)
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
    and real-time attack mitigation.
    """)
    
    st.divider()
    
    # Sidebar - Mode Selection
    st.sidebar.header("🎛️ Mode Selection")
    
    mode = st.sidebar.radio(
        "Operation Mode",
        ["Single Run", "Adaptive Multi-Round", "Strategy Comparison", "Static vs Adaptive"],
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
    
    run_button = st.sidebar.button("🚀 Run Adaptive Experiment", type="primary")
    
    if run_button:
        with st.spinner(f"Running {num_rounds} adaptive rounds..."):
            result = run_adaptive_experiment(
                num_rounds=num_rounds,
                qubits_per_round=num_qubits,
                eve_enabled=eve_enabled,
                eve_probability=eve_probability,
                strategy=strategy,
                learning_rate=learning_rate,
                initial_signal=init_signal,
                initial_decoy=init_decoy,
                initial_vacuum=init_vacuum
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
            mean_key_rate = result['controller_stats']['mean_key_rate']
            st.metric("Mean Key Rate", f"{mean_key_rate:.3f}")
        
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
        
        # Visualizations
        st.header("📈 Adaptive Evolution")
        
        col1, col2 = st.columns(2)
        with col1:
            fig_qber_evo = plot_adaptive_qber_evolution(result['round_results'])
            st.pyplot(fig_qber_evo)
        
        with col2:
            fig_prob_evo = plot_decoy_probability_evolution(result['round_results'])
            st.pyplot(fig_prob_evo)
        
        # Detailed Round Data
        with st.expander("📋 Detailed Round-by-Round Data"):
            import pandas as pd
            df = pd.DataFrame(result['round_results'])
            df['qber'] = df['qber'] * 100
            df = df.round(4)
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
    
    run_button = st.sidebar.button("🚀 Run Comparison", type="primary")
    
    if run_button:
        with st.spinner("Running static vs adaptive comparison..."):
            result = run_static_vs_adaptive_comparison(
                num_rounds=num_rounds,
                qubits_per_round=num_qubits,
                eve_probability=eve_probability,
                adaptive_strategy=adaptive_strategy,
                trials=trials
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
        
        with col2:
            st.subheader("🔄 Adaptive Mode")
            st.metric("Mean QBER", f"{result['adaptive']['mean_qber']*100:.2f}%")
            st.metric("Mean Key Length", f"{result['adaptive']['mean_key_length']:.0f} bits")
        
        # Improvement metrics
        st.header("📈 Performance Improvement")
        col1, col2 = st.columns(2)
        with col1:
            qber_improvement = result['improvement']['qber_reduction']
            st.metric("QBER Reduction", f"{qber_improvement:.1f}%", 
                     delta=f"{qber_improvement:.1f}%", delta_color="inverse")
        with col2:
            key_improvement = result['improvement']['key_length_increase']
            st.metric("Key Length Increase", f"{key_improvement:.1f}%",
                     delta=f"{key_improvement:.1f}%")
        
        # Visualization
        fig_sva = plot_static_vs_adaptive(result)
        st.pyplot(fig_sva)
        
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
            
            **Conclusion:**
            The adaptive {adaptive_strategy} strategy demonstrates 
            {'superior' if qber_improvement > 0 else 'comparable'} performance
            to static decoy-state allocation, with particular strength in
            {'QBER minimization' if qber_improvement > key_improvement else 'key rate optimization'}.
            
            This validates the adaptive approach for dynamic channel conditions.
            """)


if __name__ == "__main__":
    main()