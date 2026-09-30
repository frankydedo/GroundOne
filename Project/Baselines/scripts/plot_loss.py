import re
import matplotlib.pyplot as plt
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, required=True, help="Path to the training log file")
    parser.add_argument("--out", type=str, required=True, help="Path to save the plot image")
    parser.add_argument("--title", type=str, default="LoRA Fine-tuning Loss", help="Title for the plot")
    args = parser.parse_args()

    iters = []
    train_loss = []
    val_iters = []
    val_loss = []

    with open(args.log, 'r') as f:
        for line in f:
            # Match train loss
            m = re.search(r"Iter (\d+): Train loss ([0-9.]+)", line)
            if m:
                iters.append(int(m.group(1)))
                train_loss.append(float(m.group(2)))
            
            # Match val loss
            m2 = re.search(r"Iter (\d+): Val loss ([0-9.]+)", line)
            if m2:
                val_iters.append(int(m2.group(1)))
                val_loss.append(float(m2.group(2)))

    plt.figure(figsize=(10, 6))
    plt.plot(iters, train_loss, label='Train Loss', alpha=0.7)
    if val_iters:
        plt.plot(val_iters, val_loss, label='Validation Loss', marker='o')

    plt.title(args.title)
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    plt.savefig(args.out, dpi=300)
    print(f"Plot saved to {args.out}")

if __name__ == "__main__":
    main()
