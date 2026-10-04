import sys
sys.path.insert(0, "src")
# pyrefly: ignore [missing-import]
from rizzo_router.engine import RizzoEngine

class MockTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

tools = [
    MockTool("get_weather", "Fetch the current weather for a given location."),
    MockTool("get_stock_price", "Fetch the current stock price for a given ticker symbol."),
    MockTool("search_web", "Search the web for general knowledge queries.")
]

queries = [
    "What is the weather like in Tokyo right now?",
    "Show me the stock price for Apple",
    "Who won the world cup in 2022?",
    "Will it rain tomorrow in New York?",
    "Search for the latest AI news"
]

engine = RizzoEngine()

print("--- Warming up Rizzo-Flow (First Call) ---")
try:
    warmup_res = engine.extract(query=queries[0], tools=tools)
    print(f"Warmup Latency: {warmup_res['latency_ms']:.2f} ms\n")
    
    latencies = []
    
    output_lines = []
    output_lines.append("--- Running Benchmark ---")
    print(output_lines[-1])
    
    for i in range(10):
        q = queries[i % len(queries)]
        res = engine.extract(query=q, tools=tools)
        lat = res['latency_ms']
        latencies.append(lat)
        line = f"Call {i+1:02d} | Chosen: {res['chosen_tool']:<15} | Latency: {lat:.2f} ms | Timing: {res.get('timing')}"
        output_lines.append(line)
        print(line)
        
    avg_lat = sum(latencies) / len(latencies)
    summary = f"\n--- Summary ---\nTotal Calls: {len(latencies)}\nAvg Latency: {avg_lat:.2f} ms\nMin Latency: {min(latencies):.2f} ms\nMax Latency: {max(latencies):.2f} ms"
    output_lines.append(summary)
    print(summary)
    
    with open("benchmark_results.txt", "w") as f:
        f.write("\n".join(output_lines) + "\n")
    print("\nResults successfully saved to benchmark_results.txt")
    
except Exception as e:
    print("Error:", e)
