"""CLI entry point for LightningRoute — mirrors rizzo-flow's serve / decide / health workflow."""

import argparse
import json
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="LightningRoute ⚡️ — O(1) tool routing via logit extraction"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    # ── serve ──────────────────────────────────────────────────────────
    serve_cmd = commands.add_parser("serve", help="Start the HTTP API server")
    serve_cmd.add_argument(
        "--model",
        default="mlx-community/Qwen2.5-0.5B-Instruct-4bit",
        help="HuggingFace model ID (default: %(default)s)",
    )
    serve_cmd.add_argument(
        "--adapter",
        default=None,
        help="Path to LoRA adapter weights (optional)",
    )
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8018)

    # ── decide (one-shot, no server) ──────────────────────────────────
    decide_cmd = commands.add_parser("decide", help="Route a single request from a JSON file")
    decide_cmd.add_argument("input", type=Path, help="JSON file with a RouterRequest payload")
    decide_cmd.add_argument("--output", type=str, default=None, help="Write result to this file")
    decide_cmd.add_argument(
        "--model",
        default="mlx-community/Qwen2.5-0.5B-Instruct-4bit",
    )
    decide_cmd.add_argument("--adapter", default=None)

    # ── schema ────────────────────────────────────────────────────────
    schema_cmd = commands.add_parser("schema", help="Print the JSON Schema for request/response")
    schema_cmd.add_argument(
        "--response", action="store_true", help="Print the response schema instead"
    )

    args = parser.parse_args()

    try:
        # ── schema (no model needed) ──────────────────────────────────
        if args.command == "schema":
            from .schemas.models import RouterRequest, RouterResponse

            obj = RouterResponse if args.response else RouterRequest
            print(json.dumps(obj.model_json_schema(), indent=2, ensure_ascii=False))
            return

        # ── serve ─────────────────────────────────────────────────────
        if args.command == "serve":
            from .engine.extractor import LogitExtractor
            from .api.server import create_app

            print("⚡️ LightningRoute — starting server")
            print(f"   Model:   {args.model}")
            print(f"   Adapter: {args.adapter or '(none)'}")
            print(f"   Bind:    http://{args.host}:{args.port}")
            print()

            extractor = LogitExtractor(
                model_id=args.model,
                adapter_path=args.adapter,
            )
            print("✅ Model loaded and ready to route!\n")

            import uvicorn

            uvicorn.run(create_app(extractor), host=args.host, port=args.port)

        # ── decide ────────────────────────────────────────────────────
        elif args.command == "decide":
            from .engine.extractor import LogitExtractor
            from .schemas.models import RouterRequest

            payload = json.loads(args.input.read_text(encoding="utf-8"))
            request = RouterRequest.model_validate(payload)

            print(f"⚡️ Loading model {args.model} …")
            extractor = LogitExtractor(
                model_id=args.model,
                adapter_path=args.adapter,
            )

            result = extractor.extract(
                query=request.query,
                tools=request.tools,
                system_prompt=request.system_prompt,
            )
            text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
                print(f"Result written to {args.output}")
            else:
                print(text, end="")

    except (ValueError, OSError, ImportError) as error:
        print(f"lightning-route: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
