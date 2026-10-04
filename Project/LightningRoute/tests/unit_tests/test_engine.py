import sys
import os
from pprint import pprint

# Ensure we can import the src module from the tests directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from lightning_route.engine.extractor import LogitExtractor

def main():
    print("⚡️ Initializing LightningRoute Engine...")
    
    # Read model paths from environment variables for dynamic loading
    model_id = os.environ.get("ROUTER_MODEL_ID", "/Users/francescodedominicis/Desktop/THESIS/Project/LightningRoute/models/Qwen2.5-0.5B-Instruct-MLX-8bit")
    adapter_path = os.environ.get("ROUTER_ADAPTER_PATH", "/Users/francescodedominicis/Desktop/THESIS/Project/LightningRoute/models/adapters_0.5B")
    
    if adapter_path and not os.path.exists(adapter_path):
        print(f"⚠️ Warning: Adapter not found at {adapter_path}")
        print("Proceeding without adapter (or double check your paths).")

    extractor = LogitExtractor(model_id=model_id, adapter_path=adapter_path)
    print(f"✅ Model loaded successfully! (Base: {model_id})\n")
    
    tools = [
        {"name": "FlightBooker", "description": "Books flights between cities on a given date."},
        {"name": "HotelFinder", "description": "Finds available hotels in a city."},
        {"name": "WeatherAPI", "description": "Fetches current weather for a specific location."}
    ]

    print("-" * 50)
    print("🧪 TEST 1: Direct Semantic Match")
    print("-" * 50)
    query_1 = "I need to fly from Rome to London next Friday."
    print(f"User Query: '{query_1}'")
    
    res_1 = extractor.extract(query=query_1, tools=tools)
    
    print("\nResult:")
    pprint(res_1)
    print(f"👉 Expected: FlightBooker | Got: {res_1['chosen_tool']}")
    print(f"⏱️ Latency: {res_1['latency_ms']:.2f} ms")


    print("\n" + "-" * 50)
    print("🧪 TEST 2: Epistemic Honesty (Abstain / Z)")
    print("-" * 50)
    query_2 = "What is the capital of France?"
    print(f"User Query: '{query_2}'")
    
    res_2 = extractor.extract(query=query_2, tools=tools)
    
    print("\nResult:")
    pprint(res_2)
    print(f"👉 Expected: Abstain | Got: {res_2['chosen_tool']}")
    print(f"⏱️ Latency: {res_2['latency_ms']:.2f} ms")


if __name__ == "__main__":
    main()
