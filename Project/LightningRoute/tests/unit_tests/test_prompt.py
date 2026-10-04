import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from lightning_route.engine.extractor import LogitExtractor
model_id = "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit"
adapter_path = "../LoRA_Finetuning/training_results/v2/0.5B_model_opt/adapters"
extractor = LogitExtractor(model_id, adapter_path)
prompt, mapping = extractor._format_prompt("I need to fly from Rome to London next Friday.", [
    {"name": "FlightBooker", "description": "Books flights between cities on a given date."},
    {"name": "HotelFinder", "description": "Finds available hotels in a city."},
    {"name": "WeatherAPI", "description": "Fetches current weather for a specific location."}
])
print("=== PROMPT ===")
print(prompt)
print("==============")
