import json
import urllib.request
import string
import random
import os

# Endpoint Hugging Face per il dataset BFCL
BASE_URL = "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/resolve/main"
DATASET_FILE = "BFCL_v3_simple.json"
ANSWER_FILE = "possible_answer/BFCL_v3_simple.json"
IRRELEVANCE_FILE = "BFCL_v3_irrelevance.json" # Per gli Abstain

# Template di sistema per Jev-like
SYSTEM_PROMPT = """Sei un router intelligente. Il tuo compito è analizzare la richiesta dell'utente e scegliere l'UNICO strumento (tool) corretto tra quelli disponibili.
Devi rispondere ESCLUSIVAMENTE con la lettera associata al tool scelto (es. A, B, C...).
Se la richiesta dell'utente NON può essere soddisfatta da nessuno dei tool elencati, devi rispondere con la lettera Z (Abstain)."""

def fetch_jsonl(url):
    print(f"Scaricando: {url}")
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
    prompt += f"RICHIESTA:\n{question}\n\nTOOLS DISPONIBILI:\n"
    
    for letter, tool in letter_mapping.items():
        if letter == 'Z':
            continue # Non printiamo Z come tool testuale, è implicito nelle regole.
        prompt += f"[{letter}] {tool['name']}: {tool['description']}\n"
    
    prompt += "<|im_end|>\n<|im_start|>assistant\n"
    return prompt

def process_data():
    print("Iniziando la Fase 1: Creazione del Dataset 'Typed Decisions'...\n")
    
    # 1. Scarichiamo i dati positivi (c'è una risposta)
    prompts_data = fetch_jsonl(f"{BASE_URL}/{DATASET_FILE}")
    answers_data = fetch_jsonl(f"{BASE_URL}/{ANSWER_FILE}")
    
    # Mappiamo le risposte per ID
    answers_map = {}
    for item in answers_data:
        if "id" in item and "ground_truth" in item:
            answers_map[item["id"]] = item["ground_truth"]

    dataset_mlx = []

    print(f"Processando {len(prompts_data)} esempi positivi...")
    for item in prompts_data:
        item_id = item["id"]
        # In BFCL le question sono array di messaggi
        question = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
        tools = item["function"]
        
        # Se non c'è la risposta saltiamo
        if item_id not in answers_map:
            continue
            
        ground_truth_tool_name = answers_map[item_id]
        if isinstance(ground_truth_tool_name, list):
            # In BFCL_simple a volte l'answer è la stringa intera della funzione
            if len(ground_truth_tool_name) > 0 and type(ground_truth_tool_name[0]) == str:
                 pass
            elif len(ground_truth_tool_name) > 0:
                 ground_truth_tool_name = list(ground_truth_tool_name[0].keys())[0]

        # Evitiamo parsing troppo complessi se l'answer non è pulita
        if not isinstance(ground_truth_tool_name, str):
            continue
            
        # Troviamo quale tool corrisponde al ground truth
        # Per semplicità, cerchiamo il nome del tool dentro la stringa di answer
        correct_tool = None
        for t in tools:
            if t["name"] in ground_truth_tool_name:
                correct_tool = t["name"]
                break
                
        if not correct_tool:
            continue
            
        # Mischiamo i tool per non far imparare la posizione
        random.shuffle(tools)
        
        # Mappiamo i tool alle lettere
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

    # 2. Scarichiamo i dati negativi (Irrelevance -> Abstain)
    print("\nScaricando esempi di Irrelevance (Abstain/Z)...")
    irrelevance_data = fetch_jsonl(f"{BASE_URL}/{IRRELEVANCE_FILE}")
    
    print(f"Processando {len(irrelevance_data)} esempi di Abstain...")
    for item in irrelevance_data:
        question = item["question"][0][0]["content"] if isinstance(item["question"][0], list) else item["question"][0]["content"]
        tools = item["function"]
        
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

    # Mischiamo il dataset finale
    random.shuffle(dataset_mlx)
    
    # Dividiamo in Train (80%), Val (10%), Test (10%)
    n = len(dataset_mlx)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)
    
    train_data = dataset_mlx[:train_end]
    val_data = dataset_mlx[train_end:val_end]
    test_data = dataset_mlx[val_end:]
    
    print(f"\nSalvataggio file JSONL completato!")
    print(f"Train: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    
    def save_jsonl(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
    save_jsonl(train_data, "data/processed/train.jsonl")
    save_jsonl(val_data, "data/processed/valid.jsonl")
    save_jsonl(test_data, "data/processed/test.jsonl")
    print("File salvati in data/processed/")

if __name__ == "__main__":
    process_data()
