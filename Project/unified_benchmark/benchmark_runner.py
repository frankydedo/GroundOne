import json
import re
import requests
import time
# pyrefly: ignore [missing-import]
import numpy as np
from server_wrapper import ServerWrapper

DATASET_PATH = "/Users/francescodedominicis/Desktop/THESIS/Project/data/v3_dataset/v3_test.jsonl"
OUTPUT_FILE = "/Users/francescodedominicis/Desktop/THESIS/Project/unified_benchmark/benchmark_results.json"

CONFIGS = [
    {
        "pipeline": "lightning",
        "name": "LightningRoute_0.5B",
        "model_id": "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/0.5B_model_opt/adapters"
    },
    {
        "pipeline": "lightning",
        "name": "LightningRoute_3B",
        "model_id": "lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/3B_model_opt/adapters"
    },
    {
        "pipeline": "lightning",
        "name": "LightningRoute_7B",
        "model_id": "mlx-community/Qwen2.5-7B-Instruct-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/7B_model_opt/adapters"
    },
    {
        "pipeline": "llm",
        "name": "LLM_0.5B_Base",
        "model_id": "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
        "adapter_path": None
    },
    {
        "pipeline": "llm",
        "name": "LLM_0.5B_Finetuned",
        "model_id": "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/0.5B_model_opt/adapters"
    },
    {
        "pipeline": "llm",
        "name": "LLM_3B_Base",
        "model_id": "lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit",
        "adapter_path": None
    },
    {
        "pipeline": "llm",
        "name": "LLM_3B_Finetuned",
        "model_id": "lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/3B_model_opt/adapters"
    },
    {
        "pipeline": "llm",
        "name": "LLM_7B_Base",
        "model_id": "mlx-community/Qwen2.5-7B-Instruct-8bit",
        "adapter_path": None
    },
    {
        "pipeline": "llm",
        "name": "LLM_7B_Finetuned",
        "model_id": "mlx-community/Qwen2.5-7B-Instruct-8bit",
        "adapter_path": "/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/7B_model_opt/adapters"
    },
    {
        "pipeline": "rizzo",
        "name": "RizzoFlow_Native",
        "model_id": None, # Rizzo-Flow handles its own loading via its native CLI
        "adapter_path": None
    }
]

def parse_dataset():
    buckets = {}
    with open(DATASET_PATH, 'r') as f:
        for line in f:
            data = json.loads(line)
            bucket = data["bucket"]
            text = data["text"]
            
            # Extract query
            query_match = re.search(r"REQUEST:\n(.*?)\n\nAVAILABLE TOOLS:", text, re.DOTALL)
            if not query_match:
                continue
            query = query_match.group(1).strip()
            
            # Extract tools
            tools_block_match = re.search(r"AVAILABLE TOOLS:\n(.*?)\n<\|im_end\|>", text, re.DOTALL)
            tools_block = tools_block_match.group(1) if tools_block_match else ""
            
            tools = []
            tool_letter_to_name = {}
            for line_item in tools_block.split('\n'):
                match = re.match(r"\[([A-Z])\]\s+([^:]+):\s+(.*)", line_item.strip())
                if match:
                    letter, t_name, t_desc = match.groups()
                    tools.append({"name": t_name.strip(), "description": t_desc.strip()})
                    tool_letter_to_name[letter] = t_name.strip()
                    
            # Extract Ground Truth
            gt_match = re.search(r"<\|im_start\|>assistant\n([A-Z])", text)
            if not gt_match:
                continue
            gt_letter = gt_match.group(1)
            
            gt_name = tool_letter_to_name.get(gt_letter, "Abstain")
            
            payload = {
                "query": query,
                "tools": tools,
            }
            
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append({
                "payload": payload,
                "ground_truth": gt_name
            })
            
    # For speed during development, we limit to 10 items per bucket if we want.
    # Here we run all of them.
    return buckets

def run_benchmark():
    buckets = parse_dataset()
    results = {}
    
    # Optional: limit number of items per bucket if benchmark takes too long
    # for b in buckets: buckets[b] = buckets[b][:20] 

    for config in CONFIGS:
        print(f"\n=============================================")
        print(f"Starting benchmark for {config['name']}")
        print(f"=============================================")
        
        wrapper = ServerWrapper(config['pipeline'], config['model_id'], config['adapter_path'])
        wrapper.start()
        
        config_results = {}
        
        for bucket_name, items in sorted(buckets.items()):
            print(f"  Testing Bucket: {bucket_name} ({len(items)} items)")
            
            latencies = []
            correct = 0
            
            for item in items:
                start_time = time.time()
                try:
                    if config["pipeline"] == "rizzo":
                        criteria = {t["name"]: t["description"] for t in item["payload"]["tools"]}
                        payload = {
                            "state": item["payload"]["query"],
                            "questions": {
                                "router_query": {
                                    "type": "choice",
                                    "instructions": "Choose the correct tool for the query. Reply with 'noul' if none match.",
                                    "criteria": criteria
                                }
                            }
                        }
                        resp = requests.post("http://127.0.0.1:8017/v1/decisions", json=payload, timeout=60)
                        resp.raise_for_status()
                        data = resp.json()
                        chosen_tool = data.get("answers", {}).get("router_query", "Abstain")
                        if chosen_tool == "noul" or not chosen_tool:
                            chosen_tool = "Abstain"
                    else:
                        resp = requests.post("http://127.0.0.1:8000/v1/systemone", json=item["payload"], timeout=60)
                        resp.raise_for_status()
                        data = resp.json()
                        chosen_tool = data.get("chosen_tool")
                    
                    if chosen_tool and chosen_tool.lower() == item["ground_truth"].lower():
                        correct += 1
                        
                except Exception as e:
                    print(f"    Error on request: {e}")
                    continue
                    
                end_time = time.time()
                latencies.append((end_time - start_time) * 1000)
                
            accuracy = (correct / len(items)) * 100 if items else 0
            p50 = np.percentile(latencies, 50) if latencies else 0
            p90 = np.percentile(latencies, 90) if latencies else 0
            p99 = np.percentile(latencies, 99) if latencies else 0
            
            config_results[bucket_name] = {
                "accuracy": accuracy,
                "p50_ms": p50,
                "p90_ms": p90,
                "p99_ms": p99,
                "total_tested": len(latencies)
            }
            
            print(f"    -> Acc: {accuracy:.2f}% | p50: {p50:.2f}ms | p90: {p90:.2f}ms | p99: {p99:.2f}ms")
            
            # Incremental save for live dashboard
            results[config["name"]] = config_results
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(results, f, indent=2)
            
        wrapper.stop()
        
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ All benchmarks finished. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_benchmark()
