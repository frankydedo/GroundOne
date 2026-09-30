from fastapi import FastAPI, HTTPException
import uvicorn
from contextlib import asynccontextmanager

from lightning_route.schemas.models import RouterRequest, RouterResponse
from lightning_route.engine.extractor import LogitExtractor

# Global reference to the extractor
extractor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the model into memory once when the server starts
    global extractor
    print("⚡️ Booting up LightningRoute...")
    # NOTE: These paths should be configurable via env vars or CLI arguments
    extractor = LogitExtractor(
        model_id="lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
        adapter_path="../../training_results/v2/0.5B_model_opt/adapters"
    )
    print("✅ Model loaded and ready to route!")
    
    yield
    
    # Shutdown
    print("Shutting down LightningRoute...")

app = FastAPI(
    title="LightningRoute ⚡️",
    description="A blazing-fast System One Router powered by MLX",
    version="0.1.0",
    lifespan=lifespan
)

@app.post("/v1/systemone", response_model=RouterResponse)
async def route_request(request: RouterRequest):
    """
    Takes a query and a list of tools, and returns the highest confidence routing decision
    instantly by skipping autoregressive text generation.
    """
    try:
        result = extractor.extract(
            query=request.query,
            tools=request.tools,
            system_prompt=request.system_prompt
        )
        return RouterResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("lightning_route.api.server:app", host="0.0.0.0", port=8000, reload=True)
