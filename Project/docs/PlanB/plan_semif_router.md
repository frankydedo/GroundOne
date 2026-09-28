# Implementation Plan: SemIf-Router (Ultra-fast Agentic MCP Router)

## Obiettivo
Dimostrare che un modello System One (SemIf) può abbattere drasticamente la latenza del "tool-calling" nei framework multi-agente, prendendo decisioni di routing in frazioni di secondo su hardware Apple Silicon locale.

## Modelli e Hardware
- **Hardware:** MacBook Pro Apple Silicon (16GB Unified Memory).
- **Modelli Base:** 
  - `Qwen/Qwen3.5-4B` (modello principale, ideale equilibrio tra intelligenza e consumo di memoria, ~8GB in BF16).
  - `Qwen/Qwen2.5-0.5B` o `openbmb/MiniCPM5-2B` (modelli ultra-compatti per l'analisi del trade-off prestazioni/latenza).
- **Backend:** `mlx` (nativo Apple) tramite la flag `--backend mlx` di SemIf.

## Dataset
- **Berkeley Function Calling Leaderboard (BFCL)** (sottoinsieme): Un benchmark standard per testare l'accuratezza dei modelli nella scelta dei tool. Verranno utilizzati solo i task a singolo step (identificare il tool corretto e i parametri basilari).
- Alternativa: **ToolBench** (sottoinsieme limitato).

## Metodologia Operativa
Il progetto si svilupperà in 3 fasi principali:

### Fase 1: Sviluppo della Baseline (Tool Caller Generativo via LM Studio)
- Tramite **LM Studio** verrà eseguito il modello generativo di base, caricando direttamente i pesi in formato nativo `MLX` di `Qwen3.5-4B` invece dei classici GGUF. LM Studio esporrà un server locale compatibile con le API di OpenAI (es. `http://localhost:1234/v1`).
- Verrà implementato uno script Python che invia una richiesta HTTP al server, fornendo il prompt e la lista dei tool disponibili (simulando l'API `tools`).
- **Nota bene:** L'LLM *non* eseguirà realmente i tool. Si limiterà a generare in output il JSON con il nome del tool e i parametri scelti (es. `{"name": "get_weather", "arguments": {"location": "Rome"}}`). L'obiettivo è unicamente misurare la latenza di questa decisione, pertanto non è necessaria l'esecuzione effettiva dei tool.

### Fase 2: Sviluppo del Router SemIf (System One)
- Verrà sviluppato un secondo script basato sul framework `SemIf`.
- Sarà implementato un "Prompt Formatter" che tradurrà le descrizioni JSON dei tool in "Opzioni testuali" (es. `Opzione 1: Usa la calcolatrice per fare una somma. Opzione 2: Cerca sul web.`).
- Il prompt dell'utente verrà configurato come "State" e processato (prefill) una sola volta.
- SemIf non genererà output JSON, ma valuterà le opzioni in parallelo, restituendo in modo istantaneo l'ID dell'opzione con la probabilità più alta (es. `Opzione 2: 99.8%`).

### Fase 3: Confronto e Benchmarking
- Verrà utilizzato un dataset di test estratto dalla *Berkeley Function Calling Leaderboard*.
- I due script (Baseline e Router SemIf) saranno eseguiti sullo stesso set di dati per un confronto diretto.
- Saranno registrate le seguenti metriche fondamentali:
  - **Latenza (Speed):** Il tempo necessario per identificare il tool da utilizzare (dimostrando la riduzione della latenza da secondi a millisecondi).
  - **Accuratezza (Recall@1):** La capacità di SemIf di selezionare il tool corretto mantenendo un livello di accuratezza paragonabile al modello generativo.

## Esperimenti e Metriche
- **Esperimento 1: Latenza (Speed Test)**
  - Misurazione del TTFT (Time To First Token) e dell'End-to-End Latency di SemIf confrontato con un LLM generativo interrogato tramite LM Studio (es. Qwen3.5-4B in formato MLX).
  - *Obiettivo:* Dimostrare un salto prestazionale da secondi a millisecondi.
- **Esperimento 2: Accuratezza (Recall)**
  - Esecuzione sul sottoinsieme BFCL.
  - Misurazione della **Recall@1**: la frequenza con cui il modello SemIf seleziona il tool corretto rispetto alle etichette di validazione (ground truth).
- **Esperimento 3: Scalabilità Opzioni**
  - Misurazione della latenza al variare del numero di tool disponibili (es. 5, 20, 50, 100). Si stima che, grazie alla KV cache condivisa, l'incremento dei tempi di esecuzione risulti minimo (con andamento O(1) o logaritmico, in contrapposizione a quello lineare).
- **Esperimento 4: Trade-off Accuratezza vs Latenza**
  - Ripetizione dei benchmark di latenza e Recall@1 utilizzando un modello di dimensioni notevolmente inferiori (es. `Qwen2.5-0.5B` o `MiniCPM-2B`).
  - *Obiettivo:* Analizzare il grado di riduzione della precisione nella selezione del tool al di sotto del miliardo di parametri, valutando l'ulteriore guadagno in termini di latenza e consumo di memoria RAM.
