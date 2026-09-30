import json
import time
import argparse
# pyrefly: ignore [missing-import]
from mlx_lm import load, generate

def run_error_analysis(model_id, adapter_path, output_file):
    test_file = "../data/processed_512/test.jsonl"
    print(f"Loading test dataset: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = [json.loads(line) for line in f]
        
    print(f"\nLoading Model: {model_id} (Adapter: {adapter_path})")
    model, tokenizer = load(model_id, adapter_path=adapter_path)
    
    errors = []
    
    # Error categories
    stats = {
        "format_error": 0,
        "false_abstain": 0,    # Model picked Z, but there was a valid tool
        "missed_abstain": 0,   # Model picked a tool, but it should have been Z
        "wrong_tool": 0,       # Model picked tool B instead of tool A
    }
    
    total = len(test_data)
    start_time = time.time()
    for i, item in enumerate(test_data):
        if "text" in item:
            full_text = item["text"]
            prompt_end_marker = "<|im_start|>assistant\n"
            idx = full_text.rfind(prompt_end_marker)
            prompt = full_text[:idx + len(prompt_end_marker)]
            ground_truth = full_text[idx + len(prompt_end_marker):].strip()
        elif "messages" in item:
            messages = item["messages"]
            ground_truth = messages[-1]["content"].strip()
            prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
            
        prediction = generate(model, tokenizer, prompt, max_tokens=10, verbose=False).strip()
        
        # Only take the first token character for comparison in case it outputted more
        pred_char = prediction[0] if prediction else ""
        gt_char = ground_truth[0] if ground_truth else ""
        
        if pred_char != gt_char:
            error_type = ""
            if len(prediction) > 3: # If it hallucinated a long string instead of a letter
                error_type = "format_error"
                stats["format_error"] += 1
            elif pred_char == "Z" and gt_char != "Z":
                error_type = "false_abstain"
                stats["false_abstain"] += 1
            elif pred_char != "Z" and gt_char == "Z":
                error_type = "missed_abstain"
                stats["missed_abstain"] += 1
            else:
                error_type = "wrong_tool"
                stats["wrong_tool"] += 1
                
            errors.append({
                "index": i,
                "ground_truth": ground_truth,
                "prediction": prediction,
                "error_type": error_type,
                "prompt": prompt
            })
            
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{total}...")
            
    end_time = time.time()
    avg_latency_ms = ((end_time - start_time) / total) * 1000

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "model": model_id,
            "adapter": adapter_path,
            "accuracy": ((total - len(errors)) / total) * 100,
            "total_errors": len(errors),
            "avg_latency_ms": avg_latency_ms,
            "stats": stats,
            "errors": errors
        }, f, indent=4)
        
    print(f"Analysis complete. Found {len(errors)} errors. Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--adapter-path", type=str, required=False, default=None)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    
    run_error_analysis(args.model, args.adapter_path, args.out)
