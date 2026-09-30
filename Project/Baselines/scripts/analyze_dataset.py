import json

def analyze_split(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
        
    z_count = 0
    tool_count = 0
    total = len(data)
    
    for item in data:
        if "text" in item:
            full_text = item["text"]
            prompt_end_marker = "<|im_start|>assistant\n"
            idx = full_text.rfind(prompt_end_marker)
            ground_truth = full_text[idx + len(prompt_end_marker):].strip()
        elif "messages" in item:
            messages = item["messages"]
            ground_truth = messages[-1]["content"].strip()
            
        gt_char = ground_truth[0] if ground_truth else ""
        if gt_char == 'Z':
            z_count += 1
        else:
            tool_count += 1
            
    print(f"--- Analysis for {file_path} ---")
    print(f"Total Samples: {total}")
    print(f"Abstain (Z) Class: {z_count} ({z_count/total*100:.2f}%)")
    print(f"Valid Tool (A, B, C...) Class: {tool_count} ({tool_count/total*100:.2f}%)\n")

if __name__ == "__main__":
    splits = [
        "../data/processed_512/train.jsonl",
        "../data/processed_512/valid.jsonl",
        "../data/processed_512/test.jsonl"
    ]
    
    for split in splits:
        try:
            analyze_split(split)
        except FileNotFoundError:
            print(f"Warning: {split} not found.")
