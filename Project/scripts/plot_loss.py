import re
import matplotlib.pyplot as plt
import sys
import os

def plot_loss(log_file):
    iterations = []
    losses = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Match line format: "Iter 10: Train loss 1.234, Learning Rate..."
                match = re.search(r"Iter\s+(\d+):\s+Train\s+loss\s+([0-9.]+)", line)
                if match:
                    iterations.append(int(match.group(1)))
                    losses.append(float(match.group(2)))
    except FileNotFoundError:
        print(f"Error: Could not find log file {log_file}")
        sys.exit(1)
        
    if not iterations:
        print(f"No training loss data found in {log_file}.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, losses, label="Train Loss", color="blue", linewidth=2)
    plt.title("LoRA Fine-tuning Loss Curve", fontsize=14)
    plt.xlabel("Iteration", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    
    os.makedirs("training_results/0.5B_model/plots", exist_ok=True)
    save_path = "training_results/0.5B_model/plots/loss_curve.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"Successfully generated new loss curve and saved to: {save_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_loss.py <path_to_log_file>")
        sys.exit(1)
    plot_loss(sys.argv[1])
