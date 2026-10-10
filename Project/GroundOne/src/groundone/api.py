"""Local HTTP API: one resident model, serialised GPU access, no external calls.

Routes
  POST /v1/verify      native: document + answer -> per-sentence verdicts; design (b) adapters: one pass, three-way
                       label + calibrated probabilities + strict/lenient flags from one rule (D27)
  POST /v1/systemone   TypeSafe/Jev-compatible (same contract as Rizzo-Flow): state + noul/choice/score questions
  GET  /v1/models      model list for the compatible API
  GET  /health         readiness + model metadata (base model, adapter hash, prompt version, fingerprint)
  GET  /playground     single-page UI
Bearer auth is enforced on the compatible routes only if GROUNDONE_API_KEY is set (as the hosted API expects).
"""
import hmac
import os
from math import isfinite
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi import Request as HttpRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from . import __version__, compat
from .config import API_KEY_ENV
from .schema import VerifyRequest, VerifyResponse

PLAYGROUND = Path(__file__).with_name("playground.html")


def jsonable(v):
    if isinstance(v, float):
        return v if isfinite(v) else f"<{v}>"
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v if isinstance(v, (str, int, bool)) or v is None else str(v)


def create_app(engine, api_key=None):
    app = FastAPI(title="GroundOne", version=__version__,
                  description="Sentence-level groundedness verification with a local System One model (no text generation).")
    api_key = api_key if api_key is not None else os.environ.get(API_KEY_ENV)

    @app.exception_handler(RequestValidationError)
    def invalid(request: HttpRequest, error: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": jsonable(error.errors())})

    def authorize(authorization: str | None = Header(default=None)):
        if api_key and not hmac.compare_digest((authorization or "").encode(), f"Bearer {api_key}".encode()):
            raise HTTPException(status_code=401, detail="Missing or invalid API key")

    @app.get("/health")
    def health():
        cal = engine.calibration
        return {"status": "ready", "version": __version__, "model": engine.backend.metadata, "design": engine.design,
                "calibrated": cal is not None, "threshold": cal.thresholds.get("three") if cal else None}

    @app.post("/v1/verify", response_model=VerifyResponse)
    def verify(request: VerifyRequest):
        try:
            return engine.verify(request)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    @app.post("/v1/systemone", dependencies=[Depends(authorize)])
    def systemone(request: compat.SystemOneRequest):
        try:
            return engine.systemone(request)
        except compat.UnknownModel as e:
            raise HTTPException(status_code=400, detail={"error_type": "api_usage_error", "message": str(e)}) from e
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    @app.get("/v1/models", dependencies=[Depends(authorize)])
    def models():
        return compat.list_models(engine.name)

    @app.get("/playground", response_class=HTMLResponse, include_in_schema=False)
    def playground():
        return PLAYGROUND.read_text(encoding="utf-8")

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse("/playground")

    return app
