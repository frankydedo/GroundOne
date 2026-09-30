# LightningRoute ⚡️

LightningRoute is a blazing-fast "System One" API router that leverages small-scale language models (like Qwen2.5 0.5B) using MLX on Apple Silicon.

Instead of generating text autoregressively, LightningRoute acts as a pure classifier, stopping execution after a single forward pass and extracting raw token log-probabilities to confidently route requests with sub-200ms latency.

## Architecture

- **`api/`**: FastAPI REST server and routing endpoints.
- **`engine/`**: The core MLX `LogitExtractor` logic for fast parallel inference without generation overhead.
- **`schemas/`**: Pydantic models for strict JSON request/response validation.
- **`utils/`**: Shared utilities like structured logging.

## Usage

*Documentation coming soon.*
