# LightningRoute ⚡️

LightningRoute is a blazing-fast "System One" API router that leverages small-scale language models (like Qwen2.5 0.5B) using MLX on Apple Silicon.

Instead of generating text autoregressively, LightningRoute acts as a pure classifier. It stops execution after a single forward pass and extracts raw token log-probabilities to confidently route requests with sub-200ms latency. The complexity is $\mathcal{O}(1)$ with respect to the number of tools.

## Installation

LightningRoute uses `uv` for dependency management and requires a macOS machine with Apple Silicon for MLX inference.

```bash
# Clone the repository
git clone https://github.com/your-org/LightningRoute.git
cd LightningRoute

# Sync dependencies and install the CLI
uv sync
```

## Command-Line Interface

LightningRoute exposes a powerful CLI to manage inference and the server.

### `serve` - Start the API Server
Start a FastAPI server that keeps the model loaded in memory for ultra-fast routing.

```bash
uv run lightning-route serve \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --adapter path/to/your/lora-adapters \
  --port 8018
```

### `decide` - One-Shot Inference
Evaluate a single routing request directly from a JSON file, outputting the result to the console or another file.

```bash
uv run lightning-route decide input_request.json \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit
```

### `schema` - JSON Schemas
Extract the OpenAPI JSON schemas for the request and response models.

```bash
uv run lightning-route schema
uv run lightning-route schema --response
```

## HTTP API

Once `serve` is running, the following endpoints are available:

- `GET /health`: Returns the server status, loaded model ID, and adapter path.
- `POST /v1/route`: The primary routing endpoint. Accepts a JSON payload with `query` and `tools`, and returns the highest confidence tool, the raw logits, and the execution latency.
- `POST /v1/systemone`: A backward-compatible alias for `/v1/route`.

### Example API Request

```json
{
  "query": "What is the weather in Tokyo?",
  "tools": [
    {
      "name": "get_weather",
      "description": "Fetch current weather data."
    },
    {
      "name": "search_web",
      "description": "Search the internet for news."
    }
  ]
}
```

## Architecture

- **`api/`**: FastAPI REST server and endpoints, wrapping the extractor in a long-lived process.
- **`engine/`**: The core `LogitExtractor`. It runs the MLX forward pass on a dedicated thread to ensure thread-safety and prevent GPU context panics.
- **`schemas/`**: Strict Pydantic models for request/response validation.
- **`cli.py`**: The central entrypoint that ties everything together.
