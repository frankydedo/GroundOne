from fastapi import FastAPI, HTTPException
import uvicorn
import os
from contextlib import asynccontextmanager

from llm_router.schemas import RouterRequest, RouterResponse
from llm_router.engine import LLMEngine

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    model_id = os.environ.get("ROUTER_MODEL_ID", "mlx-community/Qwen2.5-7B-Instruct-8bit")
    
    print("🤖 Booting up LLM Based Router (O(L))...")
    print(f"📦 Model: {model_id}")
    
    engine = LLMEngine(model_id=model_id)
    print("✅ Model loaded!")
    yield
    print("Shutting down...")

app = FastAPI(
    title="LLM Based Router",
    description="Traditional Generative Pipeline O(L)",
    version="0.1.0",
    lifespan=lifespan
)

@app.post("/v1/systemone", response_model=RouterResponse)
async def route_request(request: RouterRequest):
    try:
        result = engine.extract(
            query=request.query,
            tools=request.tools,
            system_prompt=request.system_prompt
        )
        return RouterResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("llm_router.server:app", host="0.0.0.0", port=8000)
