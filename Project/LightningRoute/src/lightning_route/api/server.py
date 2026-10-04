"""Local HTTP API. One resident model, serialized GPU access, no text generation."""

import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .schemas.models import RouterRequest, RouterResponse, HealthResponse
from .engine.extractor import LogitExtractor


def create_app(extractor: LogitExtractor) -> FastAPI:
    """Factory that wires a loaded LogitExtractor into a FastAPI application."""

    app = FastAPI(
        title="LightningRoute ⚡️",
        version="0.1.0",
        description=(
            "O(1) tool routing via a single logit-extraction forward pass. "
            "No text generation, no autoregressive decoding."
        ),
    )

    # ── Health ─────────────────────────────────────────────────────────
    @app.get("/health", response_model=HealthResponse)
    def health():
        return HealthResponse(
            status="ready",
            model_id=extractor.model_id,
            adapter_path=extractor.adapter_path,
        )

    # ── Primary routing endpoint ──────────────────────────────────────
    @app.post("/v1/route", response_model=RouterResponse)
    def route(request: RouterRequest):
        """
        Single forward pass routing decision.
        Accepts a query + tool list, returns the chosen tool with calibrated
        probabilities in O(1) time with respect to the number of tools.
        """
        try:
            start = time.perf_counter()
            result = extractor.extract(
                query=request.query,
                tools=request.tools,
                system_prompt=request.system_prompt,
            )
            return RouterResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ── Legacy alias (same contract) ──────────────────────────────────
    @app.post("/v1/systemone", response_model=RouterResponse)
    def systemone(request: RouterRequest):
        """Backward-compatible alias for /v1/route."""
        return route(request)

    return app
