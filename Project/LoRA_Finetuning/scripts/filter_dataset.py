import json
import os
from transformers import AutoTokenizer

def filter_dataset(input_file, output_file, tokenizer, max_tokens=512):
    print(f"Filtering {input_file} (max_tokens={max_tokens})...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
        
    filtered_data = []
    dropped_count = 0
    
    for item in data:
        if "text" in item:
            text = item["text"]
            # Tokenize and check length
            tokens = tokenizer.encode(text)
            if len(tokens) <= max_tokens:
                filtered_data.append(item)
            else:
                dropped_count += 1
        elif "messages" in item:
            messages = item["messages"]
            text = tokenizer.apply_chat_template(messages, tokenize=False)
            tokens = tokenizer.encode(text)
            if len(tokens) <= max_tokens:
                filtered_data.append(item)
            else:
                dropped_count += 1
                
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in filtered_data:
            f.write(json.dumps(item) + "\n")
            
    print(f"Done! Kept: {len(filtered_data)}, Dropped: {dropped_count} ({(dropped_count/len(data))*100:.2f}%)\n")

if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
    
    splits = ["train", "valid", "test"]
    for split in splits:
        input_path = f"../data/processed/{split}.jsonl"
        output_path = f"../data/processed_512/{split}.jsonl"
        if os.path.exists(input_path):
            filter_dataset(input_path, output_path, tokenizer, max_tokens=512)
