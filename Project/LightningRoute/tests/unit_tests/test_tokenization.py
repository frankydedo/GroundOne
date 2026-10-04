from mlx_lm import load
_, tok = load("lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit")
text = "<|im_start|>system\nHello<|im_end|>\n"
print("Without allowed_special:", tok.encode(text, add_special_tokens=False))
# If it's literally string characters, the ID array will be long.
# If it's a special token, it will have the 151644 ID.
