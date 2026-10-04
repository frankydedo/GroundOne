import time
import urllib.request
import json

class RizzoEngine:
    def __init__(self, model_id: str = None):
        # We no longer load the model directly here; rizzo-flow runs as a separate API server.
        self.api_url = "http://127.0.0.1:8017/v1/decisions"
        
    def extract(self, query: str, tools: list, system_prompt: str = None):
        start_time = time.perf_counter()
        
        options = [{"id": t.name, "description": t.description} for t in tools]
        options.append({"id": "Abstain", "description": "No applicable tool."})
        
        payload = {
            "state": query,
            "questions": {
                "router_query": {
                    "type": "choice",
                    "instructions": system_prompt or "You are a tool router. Select the best tool for the query.",
                    "options": options
                }
            }
        }
        
        # Call rizzo-flow API
        req = urllib.request.Request(
            self.api_url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        # Parse response
        answers = result.get("answers", {})
        query_answer = answers.get("router_query", {})
        timing = result.get("timing", {})
        
        chosen_tool = query_answer.get("choice")
        probs_dict = query_answer.get("probabilities", {})
        confidence = probs_dict.get(chosen_tool, 0.0) if chosen_tool else 0.0
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "chosen_tool": chosen_tool,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "logits": probs_dict,
            "timing": timing
        }
