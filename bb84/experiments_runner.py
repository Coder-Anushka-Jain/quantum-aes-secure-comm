import numpy as np
from bb84.experiments import run_bb84_with_eve

def run_eve_sweep(
    num_qubits=32,
    eve_probs=[0.0, 0.25, 0.5, 0.75, 1.0],
    trials=3
):
    results = []

    for p in eve_probs:
        qbers = []
        key_lengths = []

        for _ in range(trials):
            out = run_bb84_with_eve(
                num_qubits=num_qubits,
                eve_probability=p
            )
            qbers.append(out["qber"])
            key_lengths.append(len(out["alice_key"]))

        results.append({
            "eve_prob": p,
            "avg_qber": np.mean(qbers),
            "avg_key_length": np.mean(key_lengths)
        })

    return results
