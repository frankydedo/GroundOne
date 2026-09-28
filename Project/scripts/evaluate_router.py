import json
import time
from mlx_lm import load, generate

def evaluate():
    print("Loading model and LoRA adapters...")
    # Load base model and apply the trained LoRA adapters
    model, tokenizer = load("Qwen/Qwen2.5-0.5B-Instruct", adapter_path="training_results/0.5B_model/adapters")
    
    test_file = "data/processed/test.jsonl"
    print(f"Loading test dataset: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = [json.loads(line) for line in f]
        
    correct = 0
    total = len(test_data)
    
    print(f"\nStarting evaluation on {total} samples...")
    start_time = time.time()
    
    for i, item in enumerate(test_data):
        full_text = item["text"]
        
        # Split prompt and ground truth
        # The prompt is everything up to <|im_start|>assistant\n
        # The ground truth is the single letter after it
        prompt_end_marker = "<|im_start|>assistant\n"
        idx = full_text.rfind(prompt_end_marker)
        
        prompt = full_text[:idx + len(prompt_end_marker)]
        ground_truth = full_text[idx + len(prompt_end_marker):].strip()
        
        # Generate prediction (we only need 1 token since the output is a single letter A, B, C, or Z)
        prediction = generate(model, tokenizer, prompt, max_tokens=1, verbose=False).strip()
        
        if prediction == ground_truth:
            correct += 1
            
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{total} - Current Accuracy: {(correct/(i+1))*100:.2f}%")
            
    end_time = time.time()
    latency = end_time - start_time
    
    accuracy = (correct / total) * 100
    
    print("\n" + "="*40)
    print("EVALUATION RESULTS (Qwen2.5-0.5B + LoRA)")
    print("="*40)
    print(f"Total Samples: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Final Accuracy: {accuracy:.2f}%")
    print(f"Total Inference Time: {latency:.2f} seconds")
    print(f"Average Latency per prompt: {(latency/total)*1000:.2f} ms")
    print("="*40)

if __name__ == "__main__":
    evaluate()
