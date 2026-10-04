import json
import urllib.request
import string
import random
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/resolve/main"
DATASETS = ["BFCL_v3_simple.json", "BFCL_v3_multiple.json"]
ANSWERS = ["possible_answer/BFCL_v3_simple.json", "possible_answer/BFCL_v3_multiple.json"]
IRRELEVANCE_FILES = ["BFCL_v3_irrelevance.json"]

SYSTEM_PROMPT = """You are an intelligent router. Your task is to analyze the user's request and choose the SINGLE correct tool from the available options.
You must reply EXCLUSIVELY with the letter associated with the chosen tool (e.g., A, B, C...).

CRITICAL RULES FOR ABSTAINING (Z):
You must reply with the letter Z (Abstain) if ANY of the following are true:
1. The user's request is purely conversational, a greeting, or a general question.
2. NONE of the provided tools are an EXACT semantic match for the user's request. Do not try to guess or force a loosely related tool."""

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

def process():
    print("Fetching BFCL data to build v3 test set...")
    all_positive_prompts = []
    all_positive_answers = []
    for ds, ans in zip(DATASETS, ANSWERS):
        all_positive_prompts.extend(fetch_jsonl(f"{BASE_URL}/{ds}"))
        all_positive_answers.extend(fetch_jsonl(f"{BASE_URL}/{ans}"))
        
    answers_map = {}
    for item in all_positive_answers:
        if "id" in item and "ground_truth" in item:
            answers_map[item["id"]] = item["ground_truth"]

    global_tools_pool = []
    global_tools_names = set()
    for item in all_positive_prompts:
        for t in item.get("function", []):
            if t["name"] not in global_tools_names:
                global_tools_names.add(t["name"])
                global_tools_pool.append(t)
                
    irr_data = fetch_jsonl(f"{BASE_URL}/{IRRELEVANCE_FILES[0]}")
    for item in irr_data:
        for t in item.get("function", []):
            if t["name"] not in global_tools_names:
                global_tools_names.add(t["name"])
                global_tools_pool.append(t)

    buckets = {
        "1-5": {"range": (2, 5)},
        "6-10": {"range": (6, 10)},
        "11-15": {"range": (11, 15)},
        "16-20": {"range": (16, 20)},
        "21-25": {"range": (21, 25)}
    }
    
    pos_items = []
    for item in all_positive_prompts:
        item_id = item["id"]
        if item_id not in answers_map: continue
        gt = get_tool_name_from_answer(answers_map[item_id])
        if not isinstance(gt, str): continue
        tools = item["function"]
        correct_tool = next((t["name"] for t in tools if t["name"] in gt), None)
        if not correct_tool: continue
        pos_items.append((item, tools, correct_tool))
        
    random.shuffle(pos_items)
    random.shuffle(irr_data)
    
    out_data = []
    
    for bucket_name, b_info in buckets.items():
        min_n, max_n = b_info["range"]
        
        # Positive (100)
        count = 0
        for item, tools, correct_tool in pos_items:
            if count >= 100: break
            n_target = random.randint(min_n, max_n)
            tools_copy = [t for t in tools if t["name"] == correct_tool]
            current_names = {correct_tool}
            
            for t in tools:
                if len(tools_copy) >= n_target: break
                if t["name"] not in current_names:
                    tools_copy.append(t)
                    current_names.add(t["name"])
                    
            while len(tools_copy) < n_target:
                t = random.choice(global_tools_pool)
                if t["name"] not in current_names:
                    tools_copy.append(t)
                    current_names.add(t["name"])
                    
            random.shuffle(tools_copy)
            alphabet = string.ascii_uppercase
            mapping = {}
            target_letter = None
            for idx, t in enumerate(tools_copy):
                letter = alphabet[idx]
                mapping[letter] = t
                if t["name"] == correct_tool: target_letter = letter
                
            q = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
            prompt = build_prompt(q, tools_copy, mapping)
            out_data.append({"text": prompt + target_letter, "bucket": bucket_name, "type": "positive", "n_tools": n_target})
            count += 1
            
        # Abstain (100)
        count = 0
        for item in irr_data:
            if count >= 100: break
            n_target = random.randint(min_n, max_n)
            tools = item["function"]
            tools_copy = []
            current_names = set()
            
            for t in tools:
                if len(tools_copy) >= n_target: break
                if t["name"] not in current_names:
                    tools_copy.append(t)
                    current_names.add(t["name"])
            
            while len(tools_copy) < n_target:
                t = random.choice(global_tools_pool)
                if t["name"] not in current_names:
                    tools_copy.append(t)
                    current_names.add(t["name"])
                    
            random.shuffle(tools_copy)
            alphabet = string.ascii_uppercase
            mapping = {}
            for idx, t in enumerate(tools_copy):
                letter = alphabet[idx]
                mapping[letter] = t
            mapping['Z'] = "Abstain"
            
            q = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
            prompt = build_prompt(q, tools_copy, mapping)
            out_data.append({"text": prompt + "Z", "bucket": bucket_name, "type": "abstain", "n_tools": n_target})
            count += 1

    # random shuffle the final dataset so buckets are mixed
    random.shuffle(out_data)
    
    os.makedirs("../data/v3_dataset", exist_ok=True)
    out_path = "../data/v3_dataset/v3_test.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for d in out_data:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')
            
    print(f"\n🎉 v3_test.jsonl created at {out_path} with {len(out_data)} total samples (200 per bucket)!")

if __name__ == "__main__":
    process()
