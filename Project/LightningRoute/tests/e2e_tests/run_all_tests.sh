#!/bin/bash
cd /Users/francescodedominicis/Desktop/THESIS/Project/LightningRoute
source /Users/francescodedominicis/Desktop/THESIS/Project/.venv/bin/activate

RESULTS_FILE="tests/e2e_tests/all_results_summary.txt"
# Clear the results file before starting
> $RESULTS_FILE

wait_for_server() {
  echo "Waiting for server to boot..."
  for i in {1..120}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null; then
      echo "Server is up!"
      sleep 2  # Give it an extra 2 seconds to settle
      return 0
    fi
    sleep 1
  done
  echo "Server failed to boot in time."
  return 1
}

run_test() {
  local MODEL_NAME=$1
  
  echo "=====================================" | tee -a $RESULTS_FILE
  echo "Testing $MODEL_NAME" | tee -a $RESULTS_FILE
  echo "=====================================" | tee -a $RESULTS_FILE
  
  python -m uvicorn lightning_route.api.server:app --port 8000 &
  SERVER_PID=$!
  
  if wait_for_server; then
    python tests/e2e_tests/test_api.py
    
    echo "Results for $MODEL_NAME:" >> $RESULTS_FILE
    cat tests/e2e_tests/e2e_test_results.json >> $RESULTS_FILE
    echo -e "\n\n" >> $RESULTS_FILE
  else
    echo "ERROR: Could not test $MODEL_NAME because server failed to boot." >> $RESULTS_FILE
    echo -e "\n\n" >> $RESULTS_FILE
  fi
  
  echo "Killing server..."
  kill $SERVER_PID
  wait $SERVER_PID 2>/dev/null
  sleep 5
}

export PYTHONPATH=src

export ROUTER_MODEL_ID="lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit"
export ROUTER_ADAPTER_PATH="/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/0.5B_model_opt/adapters"
run_test "0.5B Model"

export ROUTER_MODEL_ID="lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit"
export ROUTER_ADAPTER_PATH="/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/3B_model_opt/adapters"
run_test "3B Model"

export ROUTER_MODEL_ID="mlx-community/Qwen2.5-7B-Instruct-8bit"
export ROUTER_ADAPTER_PATH="/Users/francescodedominicis/Desktop/THESIS/Project/LoRA_Finetuning/training_results/v2/7B_model_opt/adapters"
run_test "7B Model"

echo "Done. All results saved to $RESULTS_FILE"
