import time
import mlx.core as mx
from mlx_lm import load, generate

class LLMEngine:
    def __init__(self, model_id: str):
        self.model, self.tokenizer, *rest = load(model_id)
        
    def extract(self, query: str, tools: list, system_prompt: str = None):
        start_time = time.perf_counter()
        
        # Format tools
        tools_str = "\n".join([f"- {t.name}: {t.description}" for t in tools])
        
        # We use a strict prompt to force it to output ONLY the tool name, to minimize O(L) generation length
        sys_p = system_prompt or "You are a tool router. Output ONLY the EXACT NAME of the best tool from the list below, and nothing else. If none apply, output 'Abstain'."
        
        messages = [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": f"Tools:\n{tools_str}\n\nQuery: {query}\n\nSelected Tool:"}
        ]
        
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            formatted_prompt = f"{sys_p}\n\nTools:\n{tools_str}\n\nQuery: {query}\n\nSelected Tool:"
        
        # O(L) Generation
        # max_tokens is small since we only want the tool name, but generating autoregressively still incurs TTFT + decode time
        response = generate(self.model, self.tokenizer, prompt=formatted_prompt, max_tokens=15, verbose=False)
        
        # Clean up output
        chosen_tool = response.strip()
        # Fallback parsing in case it hallucinates
        valid_tools = [t.name for t in tools] + ["Abstain"]
        best_match = "Abstain"
        for t in valid_tools:
            if t.lower() in chosen_tool.lower():
                best_match = t
                break
                
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "chosen_tool": best_match,
            "confidence": 1.0,  # Generative LLMs don't provide a calibrated scalar confidence for the whole string natively
            "latency_ms": latency_ms,
            "logits": {best_match: 1.0}
        }
