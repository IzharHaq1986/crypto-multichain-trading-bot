import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_walk_forward(csv_path="walk_forward_results.csv"):
    df = pd.read_csv(csv_path)

    # Convert dates
    df["test_start"] = pd.to_datetime(df["test_start"])

    # Plot returns over time
    plt.figure(figsize=(12, 5))
    plt.plot(df["test_start"], df["return_pct"], marker="o")
    plt.axhline(0, linestyle="--")
    plt.title("Walk-Forward Out-of-Sample Returns")
    plt.xlabel("Test Window Start Date")
    plt.ylabel("Return (%)")
    plt.tight_layout()
    plt.savefig("walk_forward_returns.png", dpi=200)
    print("Saved walk_forward_returns.png")


if __name__ == "__main__":
    plot_walk_forward()
