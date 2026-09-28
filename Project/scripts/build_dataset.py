import json
import urllib.request
import string
import random
import os

BASE_URL = "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/resolve/main"
DATASETS = ["BFCL_v3_simple.json", "BFCL_v3_multiple.json", "BFCL_v3_live_simple.json", "BFCL_v3_live_multiple.json"]
ANSWERS = ["possible_answer/BFCL_v3_simple.json", "possible_answer/BFCL_v3_multiple.json", "possible_answer/BFCL_v3_live_simple.json", "possible_answer/BFCL_v3_live_multiple.json"]
IRRELEVANCE_FILES = ["BFCL_v3_irrelevance.json", "BFCL_v3_live_irrelevance.json"]

# System template for Jev-like
SYSTEM_PROMPT = """You are an intelligent router. Your task is to analyze the user's request and choose the SINGLE correct tool from the available options.
You must reply EXCLUSIVELY with the letter associated with the chosen tool (e.g., A, B, C...).
If the user's request CANNOT be satisfied by any of the listed tools, you must reply with the letter Z (Abstain)."""

def fetch_jsonl(url):
    print(f"Downloading: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    lines = content.strip().split('\n')
    data = []
    for line in lines:
        if line.strip():
            data.append(json.loads(line))
    return data

def build_prompt(question, tools, letter_mapping):
    prompt = f"<|im_start|>system\n{SYSTEM_PROMPT}\n<|im_end|>\n"
    prompt += "<|im_start|>user\n"
    prompt += f"REQUEST:\n{question}\n\nAVAILABLE TOOLS:\n"
    
    for letter, tool in letter_mapping.items():
        if letter == 'Z':
            continue 
        prompt += f"[{letter}] {tool['name']}: {tool['description']}\n"
    
    prompt += "<|im_end|>\n<|im_start|>assistant\n"
    return prompt

def get_tool_name_from_answer(ground_truth_tool_name):
    if isinstance(ground_truth_tool_name, list):
        if len(ground_truth_tool_name) > 0 and type(ground_truth_tool_name[0]) == str:
            pass
        elif len(ground_truth_tool_name) > 0 and type(ground_truth_tool_name[0]) == dict:
            ground_truth_tool_name = list(ground_truth_tool_name[0].keys())[0]
    return ground_truth_tool_name

def process_data():
    print("Starting Phase 1 (v2): Creating Robust 'Typed Decisions' Dataset...\n")
    
    all_positive_prompts = []
    all_positive_answers = []
    
    for ds, ans in zip(DATASETS, ANSWERS):
        all_positive_prompts.extend(fetch_jsonl(f"{BASE_URL}/{ds}"))
        all_positive_answers.extend(fetch_jsonl(f"{BASE_URL}/{ans}"))
        
    answers_map = {}
    for item in all_positive_answers:
        if "id" in item and "ground_truth" in item:
            answers_map[item["id"]] = item["ground_truth"]

    # Extract all unique tools globally for distractors
    global_tools_pool = []
    global_tools_names = set()
    for item in all_positive_prompts:
        for t in item.get("function", []):
            if t["name"] not in global_tools_names:
                global_tools_names.add(t["name"])
                global_tools_pool.append(t)
                
    dataset_mlx = []
    print(f"Processing {len(all_positive_prompts)} positive examples...")
    
    for item in all_positive_prompts:
        item_id = item["id"]
        question = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
        tools = item["function"]
        
        if item_id not in answers_map:
            continue
            
        ground_truth_tool_name = get_tool_name_from_answer(answers_map[item_id])
        if not isinstance(ground_truth_tool_name, str):
            continue
            
        correct_tool = None
        for t in tools:
            if t["name"] in ground_truth_tool_name:
                correct_tool = t["name"]
                break
                
        if not correct_tool:
            continue
            
        # Ensure we do not exceed 25 tools (A-Y)
        if len(tools) > 25:
            tools_without_correct = [t for t in tools if t["name"] != correct_tool]
            random.shuffle(tools_without_correct)
            tools = [t for t in tools if t["name"] == correct_tool] + tools_without_correct[:24]
            
        # Inject distractors if tools are less than 4
        current_tool_names = {t["name"] for t in tools}
        while len(tools) < 4:
            random_tool = random.choice(global_tools_pool)
            if random_tool["name"] not in current_tool_names:
                tools.append(random_tool)
                current_tool_names.add(random_tool["name"])
            
        random.shuffle(tools)
        
        alphabet = string.ascii_uppercase
        letter_mapping = {}
        target_letter = None
        
        for idx, t in enumerate(tools):
            letter = alphabet[idx]
            letter_mapping[letter] = t
            if t["name"] == correct_tool:
                target_letter = letter
                
        if not target_letter:
            continue
            
        final_prompt = build_prompt(question, tools, letter_mapping)
        dataset_mlx.append({
            "text": final_prompt + target_letter
        })

    # Abstain data
    print("\nDownloading Irrelevance (Abstain/Z) examples...")
    irrelevance_data = []
    for irr_file in IRRELEVANCE_FILES:
        irrelevance_data.extend(fetch_jsonl(f"{BASE_URL}/{irr_file}"))
    
    print(f"Processing {len(irrelevance_data)} Abstain examples...")
    for item in irrelevance_data:
        question = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
        tools = item["function"]
        
        if len(tools) > 25:
            random.shuffle(tools)
            tools = tools[:25]
            
        current_tool_names = {t["name"] for t in tools}
        while len(tools) < 4:
            random_tool = random.choice(global_tools_pool)
            if random_tool["name"] not in current_tool_names:
                tools.append(random_tool)
                current_tool_names.add(random_tool["name"])
                
        random.shuffle(tools)
        
        alphabet = string.ascii_uppercase
        letter_mapping = {}
        for idx, t in enumerate(tools):
            letter = alphabet[idx]
            letter_mapping[letter] = t
            
        letter_mapping['Z'] = "Abstain"
        
        final_prompt = build_prompt(question, tools, letter_mapping)
        dataset_mlx.append({
            "text": final_prompt + "Z"
        })

    random.shuffle(dataset_mlx)
    
    n = len(dataset_mlx)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)
    
    train_data = dataset_mlx[:train_end]
    val_data = dataset_mlx[train_end:val_end]
    test_data = dataset_mlx[val_end:]
    
    print(f"\nJSONL Save Complete!")
    print(f"Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    
    def save_jsonl(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
    save_jsonl(train_data, "data/processed/train.jsonl")
    save_jsonl(val_data, "data/processed/valid.jsonl")
    save_jsonl(test_data, "data/processed/test.jsonl")
    print("Files saved to data/processed/")

if __name__ == "__main__":
    process_data()
