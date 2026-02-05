import matplotlib.pyplot as plt
from bb84.experiments_runner import run_eve_sweep

def main():
    results = run_eve_sweep()

    eve_probs = [r["eve_prob"] for r in results]
    qbers = [r["avg_qber"] for r in results]
    key_lengths = [r["avg_key_length"] for r in results]

    # -------- QBER Plot --------
    plt.figure()
    plt.plot(eve_probs, qbers, marker="o")
    plt.xlabel("Eve Interception Probability")
    plt.ylabel("QBER")
    plt.title("QBER vs Eve Probability")
    plt.grid()
    plt.savefig("plots/qber_vs_eve.png")
    plt.show()

    # -------- Key Length Plot --------
    plt.figure()
    plt.plot(eve_probs, key_lengths, marker="s")
    plt.xlabel("Eve Interception Probability")
    plt.ylabel("Final Key Length")
    plt.title("Key Length vs Eve Probability")
    plt.grid()
    plt.savefig("plots/keylength_vs_eve.png")
    plt.show()

if __name__ == "__main__":
    main()
