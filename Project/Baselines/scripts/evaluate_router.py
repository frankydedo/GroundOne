import json
import time
# pyrefly: ignore [missing-import]
from mlx_lm import load, generate
import argparse

def run_evaluation(model, tokenizer, test_data, model_name):
    correct = 0
    total = len(test_data)
    
    print(f"\n--- Starting evaluation for {model_name} on {total} samples ---")
    start_time = time.time()
    
    for i, item in enumerate(test_data):
        if "text" in item:
            full_text = item["text"]
            prompt_end_marker = "<|im_start|>assistant\n"
            idx = full_text.rfind(prompt_end_marker)
            prompt = full_text[:idx + len(prompt_end_marker)]
            ground_truth = full_text[idx + len(prompt_end_marker):].strip()
        elif "messages" in item:
            # We assume the last message is the assistant's answer
            messages = item["messages"]
            ground_truth = messages[-1]["content"].strip()
            # Generate the prompt for all messages except the assistant's answer
            prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
        else:
            raise KeyError("Neither 'text' nor 'messages' found in test item.")
        
        prediction = generate(model, tokenizer, prompt, max_tokens=1, verbose=False).strip()
        
        if prediction == ground_truth:
            correct += 1
            
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"Processed {i + 1}/{total} - Current Accuracy: {(correct/(i+1))*100:.2f}%")
            
    end_time = time.time()
    latency = end_time - start_time
    accuracy = (correct / total) * 100
    
    print("\n" + "="*40)
    print(f"EVALUATION RESULTS: {model_name}")
    print("="*40)
    print(f"Total Samples: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Final Accuracy: {accuracy:.2f}%")
    print(f"Total Inference Time: {latency:.2f} seconds")
    print(f"Average Latency per prompt: {(latency/total)*1000:.2f} ms")
    print("="*40)
    return accuracy, latency

def evaluate(model_id, adapter_path):
    test_file = "../data/processed/test.jsonl"
    print(f"Loading test dataset: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = [json.loads(line) for line in f]
        
    print("\nLoading BASE MODEL (No LoRA)...")
    base_model, base_tokenizer = load(model_id)
    base_acc, base_lat = run_evaluation(base_model, base_tokenizer, test_data, f"BASE MODEL ({model_id})")
    
    # We must explicitly delete the model from memory to avoid OOM
    del base_model
    del base_tokenizer
    
    print("\nLoading LORA FINETUNED MODEL...")
    lora_model, lora_tokenizer = load(model_id, adapter_path=adapter_path)
    lora_acc, lora_lat = run_evaluation(lora_model, lora_tokenizer, test_data, "LORA FINETUNED MODEL")

    print("\n" + "*"*40)
    print("FINAL COMPARISON")
    print("*"*40)
    print(f"Base Model Accuracy: {base_acc:.2f}%")
    print(f"LoRA Model Accuracy: {lora_acc:.2f}%")
    print(f"Absolute Improvement:  +{lora_acc - base_acc:.2f}%")
    print("*"*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="Hugging Face model ID")
    parser.add_argument("--adapter-path", type=str, required=True, help="Path to LoRA adapters")
    args = parser.parse_args()
    
    evaluate(args.model, args.adapter_path)
