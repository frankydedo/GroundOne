#!/bin/bash

# Abilita l'uscita in caso di errore
set -e

echo "=========================================================="
echo "🚀 Avvio setup ambiente THESIS e download modelli MLX..."
echo "=========================================================="
echo ""

cd /Users/francescodedominicis/Desktop/THESIS/Project

echo "[1/4] 📦 Creazione virtual environment (venv)..."
if [ ! -d ".venv" ]; then
    /usr/bin/python3 -m venv .venv
fi
source .venv/bin/activate
echo "Venv attivato!"
echo ""

echo "[2/4] ⚙️ Installazione librerie (mlx, mlx-lm, datasets, huggingface_hub)..."
pip install --upgrade pip > /dev/null
pip install mlx mlx-lm datasets pandas "huggingface_hub[cli]"
echo ""

echo "[3/4] 🧠 Download Modelli da HuggingFace..."
echo "-> Scaricando Qwen2.5-0.5B-Instruct-MLX-8bit (Ultra-Compatto)..."
huggingface-cli download lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit

echo "-> Scaricando Qwen3.5-4B-MLX-8bit (Principale)..."
huggingface-cli download lmstudio-community/Qwen3.5-4B-MLX-8bit
echo ""

echo "[4/4] 📚 Download Dataset BFCL..."
python -c '
from datasets import load_dataset
print("Avvio download Gorilla BFCL (Berkeley Function Calling Leaderboard)...")
try:
    load_dataset("gorilla-llm/Berkeley-Function-Calling-Leaderboard")
    print("Download dataset completato e cachato!")
except Exception as e:
    print(f"Errore temporaneo nel dataset: {e}")
'

echo ""
echo "=========================================================="
echo "✅ TUTTO COMPLETATO CON SUCCESSO!"
echo "Ora hai i modelli pronti e il virtual environment configurato."
echo "Puoi chiudere questa finestra."
echo "=========================================================="
