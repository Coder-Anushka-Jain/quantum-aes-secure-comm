# BB84 Quantum-Classical Secure Communication System

## 🎯 Overview

This project implements a **hybrid quantum-classical secure communication system** combining:
- **BB84 Quantum Key Distribution (QKD)** for provably secure key exchange
- **AES-128 encryption** for efficient message encryption
- **Interactive visualization** via Streamlit UI
- **Eavesdropping detection** using intercept-resend attack simulation

This is a research-grade implementation suitable for **conference presentations**, **academic papers**, and **cryptography education**.

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     BB84 PROTOCOL LAYER                      │
│  ┌─────────┐      ┌──────────┐      ┌─────────┐            │
│  │  Alice  │─────▶│   Eve    │─────▶│   Bob   │            │
│  │(Sender) │      │(Optional)│      │(Receiver)│            │
│  └─────────┘      └──────────┘      └─────────┘            │
│       │                                    │                 │
│       └────────── Basis Reconciliation ────┘                │
│                          │                                   │
│                    Sifted Key                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 AES ENCRYPTION LAYER                         │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │ Quantum Key  │───▶│  SHA-256    │───▶│  AES-128 Key │   │
│  │ (BB84 output)│    │  Derivation │    │  (16 bytes)  │   │
│  └──────────────┘    └─────────────┘    └──────────────┘   │
│                                                │             │
│                                                ▼             │
│                          ┌──────────────────────────┐       │
│                          │  Encrypt/Decrypt Message │       │
│                          │      (CBC Mode)          │       │
│                          └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure
```
quantum-aes-secure-comm/
│
├── bb84/
│   ├── __init__.py              # Package initialization
│   ├── bb84_core.py             # Core BB84 protocol logic
│   ├── eve_attack.py            # Intercept-resend attack simulation
│   ├── experiments.py           # Experiment wrappers
│   ├── experiments_runner.py    # Parameter sweep runner
│   └── plot_results.py          # Matplotlib visualization
│
├── UI/
│   ├── __init__.py              # UI package initialization
│   └── app.py                   # Streamlit interactive application
│
├── plots/                        # Auto-generated plots (gitignored)
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd quantum-aes-secure-comm

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run UI/app.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 🎮 Usage

### Interactive UI Features

1. **Configure Parameters**
   - Adjust number of qubits (100-2000)
   - Enable/disable Eve's presence
   - Set Eve's interception probability (0-100%)
   - Enter custom message for encryption

2. **Run BB84 Protocol**
   - Click "Run BB84 Protocol" button
   - View real-time results and metrics

3. **Analyze Results**
   - QBER measurement and security threshold check
   - Quantum key preview (first 64 bits)
   - AES encryption/decryption demonstration
   - Performance graphs vs Eve probability

### Programmatic Usage
```python
from bb84.experiments_runner import run_experiment

# Run BB84 without Eve
result = run_experiment(num_qubits=1000, eve_enabled=False)

# Run BB84 with Eve
result = run_experiment(num_qubits=1000, eve_enabled=True, eve_probability=0.3)

# Access results
print(f"QBER: {result['qber']:.2%}")
print(f"Key Length: {len(result['alice_key'])} bits")
```

---

## 🔬 Research Contributions

### Novel Aspects

1. **Hybrid Architecture**: Seamless integration of quantum and classical cryptography
2. **Real-time Visualization**: Interactive demonstration of eavesdropping detection
3. **Educational Tool**: Step-by-step explanation of BB84 and AES integration
4. **Reproducible Research**: Deterministic experiments with configurable parameters

### Theoretical Foundation

- **BB84 Security**: Based on Heisenberg uncertainty principle
- **QBER Threshold**: 11% threshold for intercept-resend attack detection
- **Expected QBER**: ~25% × (Eve interception probability) for intercept-resend
- **Key Rate**: ~50% of transmitted qubits (due to basis reconciliation)

### Performance Characteristics

| Parameter | Value |
|-----------|-------|
| Basis Matching Rate | ~50% |
| QBER (no Eve) | ~0% |
| QBER (Eve at 100%) | ~25% |
| Security Threshold | 11% |
| AES Key Size | 128 bits |

---

## 🧪 Experimental Validation

The system has been validated against theoretical predictions:

- ✅ QBER scales linearly with Eve probability (slope ≈ 0.25)
- ✅ Key length remains ~50% of transmitted qubits
- ✅ Security threshold correctly identifies eavesdropping
- ✅ AES encryption/decryption maintains message integrity

---

## 📊 Example Output
```
BB84 Protocol Execution:
- Total Qubits Sent: 1000
- Matching Bases: 502
- Final Key Length: 502 bits
- QBER: 7.37%
- Status: ✅ Secure (QBER ≤ 11%)

AES-128 Encryption:
- Original: "Quantum cryptography is secure!"
- Encrypted: 3a7f2e9c1b8d4f6a...
- Decrypted: "Quantum cryptography is secure!"
```

---

## 🎓 Academic Context

This project is suitable for:

- **Conference Papers**: Demonstrating practical QKD implementations
- **Educational Workshops**: Teaching quantum cryptography concepts
- **Patent Applications**: Novel hybrid quantum-classical systems
- **Research Validation**: Experimental verification of BB84 theory

### Citation

If you use this code in academic work, please cite:
```bibtex
@software{bb84_aes_secure_comm,
  title = {BB84 Quantum-Classical Secure Communication System},
  author = {[Your Name]},
  year = {2025},
  url = {[Repository URL]}
}
```

---

## 🔐 Security Considerations

### Quantum Security
- Information-theoretic security (when QBER < 11%)
- Eavesdropping detection via QBER measurement
- No computational assumptions required

### Classical Security
- AES-128 provides 128-bit security
- CBC mode with random IV
- Key derivation via SHA-256

### Limitations
- Simulation only (no actual quantum hardware)
- No privacy amplification or error correction implemented
- Single eavesdropper model (intercept-resend only)

---

## 🛠️ Future Enhancements

- [ ] Add privacy amplification protocols
- [ ] Implement CASCADE error correction
- [ ] Support for E91 and B92 protocols
- [ ] Integration with real quantum hardware (IBM Quantum, etc.)
- [ ] Advanced attack simulations (PNS, Trojan horse)
- [ ] Real-time key rate optimization

---

## 📝 License

[Specify your license here - MIT, Apache 2.0, etc.]

---

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

---

## 📧 Contact

For questions or collaboration inquiries:
- Email: [your-email@example.com]
- GitHub: [your-github-username]

---

## 🙏 Acknowledgments

- Based on the BB84 protocol by Bennett & Brassard (1984)
- Inspired by quantum cryptography research at [Your Institution]
- Built with Streamlit, NumPy, and PyCryptodome

---

**⚡ Quantum-secured communication for the future. ⚡**