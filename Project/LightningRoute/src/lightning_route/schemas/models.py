from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ToolDescription(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None

class RouterRequest(BaseModel):
    query: str = Field(..., description="The user's input query to route.")
    tools: List[ToolDescription] = Field(..., description="List of available tools to choose from.")
    system_prompt: Optional[str] = Field(None, description="Optional custom system prompt. If None, the default is used.")

class RouterResponse(BaseModel):
    chosen_tool: str = Field(..., description="The name of the chosen tool, or 'Z' for Abstain.")
    confidence: float = Field(..., description="The softmax confidence score (0.0 to 1.0) of the decision.")
    latency_ms: float = Field(..., description="Time taken to process the forward pass in milliseconds.")
    logits: Dict[str, float] = Field(..., description="Raw probability distribution across valid options.")
