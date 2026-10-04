import time
import string
import mlx.core as mx
from mlx_lm import load, generate

DEFAULT_SYSTEM_PROMPT = """You are an intelligent router. Your task is to analyze the user's request and choose the SINGLE correct tool from the available options.
You must reply EXCLUSIVELY with the letter associated with the chosen tool (e.g., A, B, C...).

CRITICAL RULES FOR ABSTAINING (Z):
You must reply with the letter Z (Abstain) if ANY of the following are true:
1. The user's request is purely conversational, a greeting, or a general question.
2. NONE of the provided tools are an EXACT semantic match for the user's request. Do not try to guess or force a loosely related tool."""

class LLMEngine:
    def __init__(self, model_id: str, adapter_path: str = None):
        self.model, self.tokenizer, *rest = load(model_id, adapter_path=adapter_path)
        self.alphabet = string.ascii_uppercase
        
    def extract(self, query: str, tools: list, system_prompt: str = None):
        start_time = time.perf_counter()
        
        sys_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        
        prompt = f"<|im_start|>system\n{sys_prompt}\n<|im_end|>\n"
        prompt += "<|im_start|>user\n"
        prompt += f"REQUEST:\n{query}\n\nAVAILABLE TOOLS:\n"
        
        letter_mapping = {}
        for idx, tool in enumerate(tools):
            letter = self.alphabet[idx]
            
            if hasattr(tool, 'model_dump'):
                tool_dict = tool.model_dump()
            elif hasattr(tool, 'dict'):
                tool_dict = tool.dict()
            elif isinstance(tool, dict):
                tool_dict = tool
            else:
                tool_dict = {"name": getattr(tool, 'name', ''), "description": getattr(tool, 'description', '')}
                
            name = tool_dict.get('name', '')
            desc = tool_dict.get('description', '')
            
            letter_mapping[letter] = name
            prompt += f"[{letter}] {name}: {desc}\n"
            
        letter_mapping['Z'] = "Abstain"
        
        prompt += "<|im_end|>\n<|im_start|>assistant\n"
        
        # O(L) Generation - we only need 1 or 2 tokens for the letter
        response = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=2, verbose=False)
        
        # Clean up output
        chosen_letter = response.strip().upper()
        # Fallback parsing in case it hallucinates
        best_match = "Abstain"
        for letter in letter_mapping:
            if letter in chosen_letter:
                best_match = letter_mapping[letter]
                break
                
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        return {
            "chosen_tool": best_match,
            "confidence": 1.0,  # Generative LLMs don't provide a calibrated scalar confidence for the whole string natively
            "latency_ms": latency_ms,
            "logits": {best_match: 1.0}
        }
