import re
import matplotlib.pyplot as plt
import os
import argparse

def parse_log(filepath):
    iters = []
    train_loss = []
    val_iters = []
    val_loss = []
    
    with open(filepath, 'r') as f:
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
                
    return iters, train_loss, val_iters, val_loss

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log1", type=str, required=True, help="Path to the first training log file")
    parser.add_argument("--label1", type=str, default="0.5B Model", help="Label for the first log")
    parser.add_argument("--log2", type=str, required=True, help="Path to the second training log file")
    parser.add_argument("--label2", type=str, default="3B Model", help="Label for the second log")
    parser.add_argument("--log3", type=str, required=True, help="Path to the third training log file")
    parser.add_argument("--label3", type=str, default="7B Model", help="Label for the third log")
    parser.add_argument("--out", type=str, required=True, help="Path to save the plot image")
    parser.add_argument("--title", type=str, default="LoRA Fine-tuning Loss Comparison (v2)", help="Title for the plot")
    args = parser.parse_args()

    iters1, train_loss1, val_iters1, val_loss1 = parse_log(args.log1)
    iters2, train_loss2, val_iters2, val_loss2 = parse_log(args.log2)
    iters3, train_loss3, val_iters3, val_loss3 = parse_log(args.log3)

    plt.figure(figsize=(10, 6))
    
    # Plot first model
    plt.plot(iters1, train_loss1, label=f'{args.label1} Train Loss', color='blue', alpha=0.5)
    if val_iters1:
        plt.plot(val_iters1, val_loss1, label=f'{args.label1} Val Loss', marker='o', color='darkblue')

    # Plot second model
    plt.plot(iters2, train_loss2, label=f'{args.label2} Train Loss', color='green', alpha=0.5)
    if val_iters2:
        plt.plot(val_iters2, val_loss2, label=f'{args.label2} Val Loss', marker='s', color='darkgreen')

    # Plot third model
    plt.plot(iters3, train_loss3, label=f'{args.label3} Train Loss', color='red', alpha=0.5)
    if val_iters3:
        plt.plot(val_iters3, val_loss3, label=f'{args.label3} Val Loss', marker='^', color='darkred')

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
