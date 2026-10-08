#!/bin/bash
# Start Rizzo-Flow (arm64 env, Metal, fine-tuned 4B Q4_K_M), run the B3 client on the frozen tests, stop the server.
cd /Users/francescodedominicis/Desktop/THESIS/SystemOne_repos/rizzo-flow || exit 1
.venv-arm64/bin/rizzo serve --port 8017 --ctx 4096 --quant q4_k_m > /Users/francescodedominicis/Desktop/THESIS/Project/outputs/logs/rizzo_server.log 2>&1 &
SRV=$!
trap "kill $SRV 2>/dev/null" EXIT
for i in $(seq 1 120); do curl -s localhost:8017/health >/dev/null && break; sleep 2; done
cd /Users/francescodedominicis/Desktop/THESIS/Project
GroundOne/.venv/bin/groundone baselines frozen --system rizzo --url http://127.0.0.1:8017 --suite t1 --limit 300 --name rizzo-flow-4b-q4
GroundOne/.venv/bin/groundone baselines frozen --system rizzo --url http://127.0.0.1:8017 --suite t3 --limit 600 --name rizzo-flow-4b-q4
