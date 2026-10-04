import time
import string
import threading
from concurrent.futures import ThreadPoolExecutor

# pyrefly: ignore [missing-import]
import mlx.core as mx
# pyrefly: ignore [missing-import]
from mlx_lm import load

DEFAULT_SYSTEM_PROMPT = """You are an intelligent router. Your task is to analyze the user's request and choose the SINGLE correct tool from the available options.
You must reply EXCLUSIVELY with the letter associated with the chosen tool (e.g., A, B, C...).

CRITICAL RULES FOR ABSTAINING (Z):
You must reply with the letter Z (Abstain) if ANY of the following are true:
1. The user's request is purely conversational, a greeting, or a general question.
2. NONE of the provided tools are an EXACT semantic match for the user's request. Do not try to guess or force a loosely related tool."""

class LogitExtractor:
    def __init__(self, model_id: str, adapter_path: str = None):
        """
        Initializes the LogitExtractor engine.
        Loads the MLX model and tokenizer into memory on a dedicated thread.
        """
        self.model_id = model_id
        self.adapter_path = adapter_path
        
        # Protect MLX operations (Metal GPU contexts crash if thread dies)
        self._lock = threading.Lock()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mlx-inference")
        
        # Load the model on the persistent worker thread
        self.model, self.tokenizer = self._worker.submit(self._load_model).result()
        
        # Pre-compute target token IDs for the letters A-Z
        self.alphabet = string.ascii_uppercase
        self.token_id_map = {}
        for letter in self.alphabet:
            # We encode the letter without special tokens to get the exact ID
            tokens = self.tokenizer.encode(letter, add_special_tokens=False)
            if len(tokens) > 0:
                self.token_id_map[letter] = tokens[0]

    def _load_model(self):
        """Loads the model and tokenizer inside the persistent worker thread."""
        return load(self.model_id, adapter_path=self.adapter_path)

    def _format_prompt(self, query: str, tools: list, system_prompt: str = None) -> tuple[str, dict]:
        """
        Formats the input query and tools into the exact training chat template format.
        Returns the formatted string and the letter-to-tool mapping.
        """
        sys_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        
        prompt = f"<|im_start|>system\n{sys_prompt}\n<|im_end|>\n"
        prompt += "<|im_start|>user\n"
        prompt += f"REQUEST:\n{query}\n\nAVAILABLE TOOLS:\n"
        
        letter_mapping = {}
        for idx, tool in enumerate(tools):
            letter = self.alphabet[idx]
            
            # Handle both dictionary (direct engine call) and Pydantic object (API call)
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
        
        return prompt, letter_mapping

    def _forward_pass_thread(self, input_ids: list, target_token_ids: list) -> list:
        """
        Executes the single forward pass and extracts probabilities.
        MUST run inside the persistent worker thread to avoid Metal panics.
        """
        # Single forward pass for the entire prompt sequence
        # We slice [0, -1] to get the logits for the very last token position
        logits = self.model(mx.array([input_ids]))[0, -1].astype(mx.float32)
        
        # Extract only the logits corresponding to our target options (A, B, C, ..., Z)
        selected_logits = logits[mx.array(target_token_ids)]
        
        # Apply softmax to convert raw logits to calibrated probabilities
        probabilities = mx.softmax(selected_logits).tolist()
        
        mx.eval(probabilities) # Ensure lazy computation is evaluated
        return probabilities

    def extract(self, query: str, tools: list, system_prompt: str = None) -> dict:
        """
        Performs a single forward pass without autoregressive generation.
        Extracts the log probabilities for the valid tool tokens.
        """
        start_time = time.time()
        
        # 1. Format the prompt and map tools to letters
        prompt, letter_mapping = self._format_prompt(query, tools, system_prompt)
        
        # 2. Tokenize the prompt
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        
        # 3. Determine the valid token IDs to extract (only the letters we used + 'Z')
        valid_letters = list(letter_mapping.keys())
        target_token_ids = [self.token_id_map[letter] for letter in valid_letters]
        
        # 4. Execute the MLX forward pass on the protected worker thread
        with self._lock:
            probabilities = self._worker.submit(
                self._forward_pass_thread, input_ids, target_token_ids
            ).result()
        
        # 5. Map probabilities back to tool names
        logits_dict = {}
        best_tool = None
        best_prob = -1.0
        
        for i, letter in enumerate(valid_letters):
            prob = probabilities[i]
            tool_name = letter_mapping[letter]
            logits_dict[tool_name] = prob
            
            if prob > best_prob:
                best_prob = prob
                best_tool = tool_name
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000.0
        
        return {
            "chosen_tool": best_tool,
            "confidence": best_prob,
            "latency_ms": latency_ms,
            "logits": logits_dict
        }
