"""
Streamlit Application for BB84 + AES Secure Communication System

This interactive UI demonstrates:
1. BB84 Quantum Key Distribution
2. Eve's intercept-resend attack
3. AES-128 encryption using quantum-derived keys
"""

import streamlit as st
import numpy as np
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from bb84.experiments_runner import run_experiment, run_eve_sweep
from bb84.plot_results import plot_qber, plot_qber_vs_eve, plot_key_length_vs_eve
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib


# Page configuration
st.set_page_config(
    page_title="BB84 Quantum-Classical Secure Communication",
    page_icon="🔐",
    layout="wide"
)


def derive_aes_key(quantum_key: list) -> bytes:
    """
    Derive a 128-bit AES key from the quantum key using SHA-256.
    
    Args:
        quantum_key: List of bits from BB84 protocol
    
    Returns:
        16-byte AES key
    """
    # Convert bit list to byte string
    key_string = ''.join(str(bit) for bit in quantum_key)
    
    # Hash to get consistent 256-bit output, take first 128 bits for AES-128
    hash_obj = hashlib.sha256(key_string.encode())
    aes_key = hash_obj.digest()[:16]  # AES-128 requires 16 bytes
    
    return aes_key


def encrypt_message(message: str, key: bytes) -> tuple:
    """
    Encrypt a message using AES-128 in CBC mode.
    
    Args:
        message: Plaintext message
        key: 16-byte AES key
    
    Returns:
        Tuple of (ciphertext, iv)
    """
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return ct_bytes, cipher.iv


def decrypt_message(ciphertext: bytes, key: bytes, iv: bytes) -> str:
    """
    Decrypt a message using AES-128 in CBC mode.
    
    Args:
        ciphertext: Encrypted message bytes
        key: 16-byte AES key
        iv: Initialization vector
    
    Returns:
        Decrypted plaintext message
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return pt.decode('utf-8')


def main():
    # Title and description
    st.title("🔐 BB84 Quantum-Classical Secure Communication System")
    st.markdown("""
    ### Hybrid Quantum–Classical Cryptography Demo
    This system demonstrates **BB84 Quantum Key Distribution** combined with **AES-128 encryption** 
    for conference-level secure communication research.
    """)
    
    st.divider()
    
    # Sidebar controls
    st.sidebar.header("⚙️ Configuration")
    
    num_qubits = st.sidebar.slider(
        "Number of Qubits",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
        help="Total number of qubits Alice sends to Bob"
    )
    
    eve_enabled = st.sidebar.checkbox(
        "Enable Eve (Eavesdropper)",
        value=False,
        help="Simulate intercept-resend attack"
    )
    
    eve_probability = 0.0
    if eve_enabled:
        eve_probability = st.sidebar.slider(
            "Eve Interception Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            help="Probability that Eve intercepts each qubit"
        )
    
    message_input = st.sidebar.text_input(
        "Message to Encrypt",
        value="Quantum cryptography is secure!",
        help="Message to encrypt with quantum-derived AES key"
    )
    
    run_button = st.sidebar.button("🚀 Run BB84 Protocol", type="primary")
    
    # Main execution
    if run_button or 'last_result' in st.session_state:
        
        if run_button:
            with st.spinner("Running BB84 protocol..."):
                result = run_experiment(num_qubits, eve_enabled, eve_probability)
                st.session_state.last_result = result
        else:
            result = st.session_state.last_result
        
        # Section 1: BB84 Execution Status
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
        
        # Section 2: QBER Analysis
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
                st.warning("Eavesdropping detected! Key should be discarded.")
        
        with col2:
            fig_qber = plot_qber(qber_value)
            st.pyplot(fig_qber)
        
        # Section 3: Quantum Key Preview
        st.header("3️⃣ Quantum Key Preview")
        
        alice_key = result['alice_key']
        bob_key = result['bob_key']
        
        if len(alice_key) >= 64:
            preview_bits = 64
            alice_preview = alice_key[:preview_bits]
            bob_preview = bob_key[:preview_bits]
            
            st.text("Alice's Key (first 64 bits):")
            st.code(''.join(str(b) for b in alice_preview), language=None)
            
            st.text("Bob's Key (first 64 bits):")
            st.code(''.join(str(b) for b in bob_preview), language=None)
            
            if alice_preview == bob_preview:
                st.success("✅ Keys match perfectly!")
            else:
                st.error("❌ Key mismatch detected!")
        else:
            st.warning(f"⚠️ Key too short ({len(alice_key)} bits). Need at least 64 bits for preview.")
        
        # Section 4: AES Encryption Demo
        st.header("4️⃣ AES-128 Encryption with Quantum Key")
        
        if len(alice_key) >= 128:
            # Derive AES key from quantum key
            aes_key = derive_aes_key(alice_key[:256] if len(alice_key) >= 256 else alice_key)
            
            st.markdown("**Derived AES-128 Key (hex):**")
            st.code(aes_key.hex(), language=None)
            
            # Encrypt message
            ciphertext, iv = encrypt_message(message_input, aes_key)
            
            # Decrypt message
            decrypted_message = decrypt_message(ciphertext, aes_key, iv)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Original Message:**")
                st.info(message_input)
            
            with col2:
                st.markdown("**Encrypted (hex):**")
                st.code(ciphertext.hex()[:100] + "..." if len(ciphertext.hex()) > 100 else ciphertext.hex(), 
                       language=None)
            
            with col3:
                st.markdown("**Decrypted Message:**")
                if decrypted_message == message_input:
                    st.success(decrypted_message)
                else:
                    st.error(decrypted_message)
            
        else:
            st.warning(f"⚠️ Insufficient key length ({len(alice_key)} bits). Need at least 128 bits for AES-128.")
        
        # Section 5: Performance Graphs
        st.header("5️⃣ Performance Analysis")
        
        with st.spinner("Generating performance plots..."):
            # Run parameter sweep
            eve_probs = np.linspace(0.0, 1.0, 11)
            sweep_results = run_eve_sweep(num_qubits=500, eve_probs=eve_probs.tolist(), trials=5)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_qber_vs_eve = plot_qber_vs_eve(sweep_results)
                st.pyplot(fig_qber_vs_eve)
            
            with col2:
                fig_key_vs_eve = plot_key_length_vs_eve(sweep_results)
                st.pyplot(fig_key_vs_eve)
        
        st.divider()
        
        # Educational notes
        with st.expander("ℹ️ About This System"):
            st.markdown("""
            ### How It Works
            
            **BB84 Protocol:**
            1. Alice generates random bits and encodes them in random bases (Z or X)
            2. Bob measures qubits in randomly chosen bases
            3. Alice and Bob publicly compare bases (but not bit values)
            4. They keep only bits where bases matched (sifted key)
            5. They measure QBER to detect eavesdropping
            
            **Eve's Attack:**
            - Eve intercepts qubits and measures in random bases
            - This collapses the quantum state and introduces errors
            - QBER increases to ~25% when Eve intercepts 100% of qubits
            - Security threshold: QBER > 11% indicates eavesdropping
            
            **AES Integration:**
            - Quantum key is hashed with SHA-256 to derive AES-128 key
            - Message is encrypted using AES in CBC mode
            - Provides information-theoretic security when QBER is acceptable
            """)


if __name__ == "__main__":
    main()