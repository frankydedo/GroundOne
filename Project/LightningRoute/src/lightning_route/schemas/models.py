from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class ToolDescription(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None


class RouterRequest(BaseModel):
    query: str = Field(..., description="The user's input query to route.")
    tools: List[ToolDescription] = Field(..., description="List of available tools to choose from.")
    system_prompt: Optional[str] = Field(
        None,
        description="Optional custom system prompt. If None, the default is used.",
    )


class RouterResponse(BaseModel):
    chosen_tool: str = Field(..., description="The name of the chosen tool, or 'Abstain'.")
    confidence: float = Field(..., description="Softmax confidence score (0.0–1.0) of the decision.")
    latency_ms: float = Field(..., description="Wall-clock time for the forward pass in milliseconds.")
    logits: Dict[str, float] = Field(..., description="Calibrated probability distribution across valid options.")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Server readiness status.")
    model_id: str = Field(..., description="HuggingFace model ID currently loaded.")
    adapter_path: Optional[str] = Field(None, description="LoRA adapter path, if any.")
