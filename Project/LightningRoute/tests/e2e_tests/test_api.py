import requests
import json
import time
import os

API_URL = "http://localhost:8000/v1/systemone"

def run_test(query: str, tools: list, test_name: str) -> dict:
    print(f"\n{'-'*50}")
    print(f"🧪 {test_name}")
    print(f"{'-'*50}")
    print(f"User Query: '{query}'")
    
    payload = {
        "query": query,
        "tools": tools
    }
    
    result_log = {
        "test_name": test_name,
        "query": query,
        "status": "failed",
        "response": None,
        "http_latency_ms": None
    }
    
    try:
        start_t = time.time()
        response = requests.post(API_URL, json=payload)
        http_latency = (time.time() - start_t) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success (HTTP 200)")
            print(f"👉 Chosen Tool: {data['chosen_tool']} (Confidence: {data['confidence']:.2%})")
            print(f"⏱️ Model Latency: {data['latency_ms']:.2f} ms")
            print(f"🌐 Total HTTP Roundtrip: {http_latency:.2f} ms")
            
            result_log["status"] = "success"
            result_log["response"] = data
            result_log["http_latency_ms"] = http_latency
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(response.text)
            result_log["error"] = f"HTTP {response.status_code}: {response.text}"
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not reach the FastAPI server.")
        result_log["error"] = "Connection Error"
        
    return result_log

def main():
    tools = [
        {
            "name": "FlightBooker", 
            "description": "Books flights between cities on a given date.",
            "parameters": {"type": "object", "properties": {"from": {"type": "string"}, "to": {"type": "string"}}}
        },
        {
            "name": "HotelFinder", 
            "description": "Finds available hotels in a city."
        },
        {
            "name": "WeatherAPI", 
            "description": "Fetches current weather for a specific location."
        }
    ]

    results = []

    # Test 1: Should abstain because mock description is vague
    results.append(run_test(
        query="I need to fly from Rome to London next Friday.",
        tools=tools,
        test_name="TEST 1: Flight Query"
    ))

    # Test 2: Should abstain clearly
    results.append(run_test(
        query="What is the capital of France?",
        tools=tools,
        test_name="TEST 2: General Knowledge (Epistemic Honesty)"
    ))
    
    # Save results to a file
    output_file = os.path.join(os.path.dirname(__file__), "e2e_test_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print(f"\n💾 Results saved to {output_file}")

if __name__ == "__main__":
    main()
