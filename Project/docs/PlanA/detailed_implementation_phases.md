# Dettaglio Implementativo delle Fasi: Custom System One Router

Questo documento espande la "Metodologia Operativa" del piano principale, dettagliando i task tecnici, gli script e gli output previsti per ogni fase del progetto.

---

## Fase 1: Preparazione del Dataset "Typed Decisions" (SFT)

**Obiettivo:** Trasformare un dataset generativo (BFCL) in un dataset di classificazione a scelta multipla, introducendo l'onestà epistemica (Abstain).

### Step Tecnici:
1. **Acquisizione Dati:** Download del subset principale del *Berkeley Function Calling Leaderboard (BFCL)*.
2. **Parser JSON (Script 1):** Scrivere uno script Python che estrae per ogni record:
   - `User Query`
   - Array di `Tools` disponibili (con relative descrizioni e parametri).
   - `Ground Truth` (il tool corretto che dovrebbe essere chiamato).
3. **Conversione in Typed Decision (Script 2):** 
   - Iniettare un Prompt di Sistema standard (es. *"Seleziona lo strumento migliore tra i seguenti:"*).
   - Assegnare dinamicamente una lettera dell'alfabeto (A, B, C...) a ogni tool.
   - Convertire il `Ground Truth` nella lettera corrispondente.
4. **Data Augmentation per Epistemic Honesty (Script 3):**
   - **Generazione Negativi:** Prendere il 20% degli esempi e rimuovere il tool corretto dall'elenco delle scelte, oppure sostituire la User Query con una domanda non correlata ai tool presenti.
   - Assegnare a questi record la label target `Z` (o un token speciale come `[ABSTAIN]`).
5. **Formattazione MLX-LM:** Esportare i dati formattati in JSONL (`train.jsonl`, `valid.jsonl`, `test.jsonl`) con i campi testuali esatti richiesti dagli script di fine-tuning di MLX.

---

## Fase 2: Ingegnerizzazione dell'Inferenza (Router Framework)

**Obiettivo:** Costruire il motore Python in grado di estrarre i logit in parallelo senza decodifica autoregressiva, esponendo un'API.

### Step Tecnici:
1. **Studio Core MLX:** Analizzare il codice sorgente di `SemIf` e la documentazione di `mlx.core` per isolare il processo del *Forward Pass*.
2. **Implementazione Motore `LogitExtractor`:**
   - Funzione che accetta lo `State` (il prompt formattato) e una lista di token target (gli ID dei token 'A', 'B', 'C', ecc. nel vocabolario Qwen).
   - Eseguire il calcolo del tensore sul Mac (GPU Apple Silicon).
   - Fermare l'esecuzione *prima* del campionamento del nuovo token.
   - Estrarre i logit grezzi unicamente per gli ID dei token target e applicare la funzione `Softmax` per normalizzarli in percentuali (0.0 -> 1.0).
3. **Ottimizzazione KV Cache:** Implementare un sistema basilare per cachare il "System Prompt" (se fisso), riducendo ulteriormente il tempo di prima valutazione.
4. **Sviluppo Server FastAPI:**
   - Creare un endpoint `POST /v1/systemone` in Python.
   - Deve accettare il formato JSON per task "Choice" (lo stesso previsto da Jev).
   - Restituire JSON contenente l'opzione vincente e l'array con le confidenze calibrate.

---

## Fase 3: LoRA Fine-Tuning in Locale (Multi-Modello)

**Obiettivo:** Addestrare i modelli Qwen quantizzati a rispondere perfettamente nel formato A-Z, ottimizzando la Cross-Entropy Loss per simulare la calibrazione.

### Step Tecnici:
1. **Setup MLX-LM:** Creare ambiente virtuale, installare `mlx` e `mlx-lm`. Assicurarsi che la pipeline LoRA funzioni correttamente con modelli a 8-bit.
2. **Training Run Modello Ultra-Compatto (0.5B):**
   - Lanciare `mlx_lm.lora` usando come base `lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit`.
   - Questo *non* è solo un test per debuggare: il modello 0.5B addestrato è parte integrante dell'esperimento (Fase 4) per mappare il trade-off latenza/accuratezza in dimensioni ridotte. Il fatto che si addestri in fretta è solo un gradito "effetto collaterale" che ci permetterà di validare velocemente la bontà del dataset.
3. **Tuning degli Iperparametri:**
   - Configurare il file `lora_config.yaml`.
   - Impostare il learning rate, il rank di LoRA (es. `r=16`), e `alpha`.
   - Assicurarsi che il parametro `train` sia impostato per limitare l'aggiornamento dei pesi a layer rilevanti (Attention, non FFN, per risparmiare memoria se necessario).
4. **Training Run Modello Principale (4B):**
   - *Importante:* Gli adapter LoRA sono legati all'architettura matematica del modello. Non puoi "riciclare" i pesi LoRA del 0.5B sul 4B.
   - Si lancia quindi un **nuovo fine-tuning LoRA (da zero, senza ereditare nulla dal 0.5B)** usando come base `lmstudio-community/Qwen3.5-4B-MLX-8bit` sullo stesso dataset.
   - Avviare il training (potrebbe richiedere diverse ore, lasciando il Mac acceso e alimentato).
5. **Adapter Merging (Per entrambi i modelli):** 
   - Usare il comando di fusione di MLX (`mlx_lm.fuse`) per fondere gli adapter LoRA del 0.5B con il suo modello base, e fare lo stesso per gli adapter del 4B con il rispettivo modello base.
   - Output: Due modelli "fusi" e indipendenti, pronti per essere confrontati nella Fase 4.

---

## Fase 4: Benchmarking e Risultati

**Obiettivo:** Quantificare scientificamente i guadagni in latenza e il trade-off accuratezza/dimensioni, consolidando il lavoro di tesi.

### Step Tecnici:
1. **Script Benchmark Latenza:**
   - Scrivere uno script che invia 100 richieste identiche al nostro server FastAPI locale.
   - Registrare il Time-To-First-Token (TTFT) e il tempo totale.
   - Calcolare Metriche: `p50`, `p90`, `p99` della latenza.
2. **Script Benchmark Baseline Generativa:**
   - Avviare LM Studio in background caricando Qwen3.5-4B (senza il nostro router).
   - Inviare tramite API OpenAI-compatible la richiesta di generare il JSON del tool calling (approccio classico Autoregressivo).
   - Misurare i tempi.
3. **Confronto Dimensionale (Trade-off):**
   - Eseguire il set di test (`test.jsonl` della Fase 1) sul modello 4B e sul modello 0.5B usando il nostro router.
   - Calcolare l'accuratezza pura (`Recall@1`: quante volte ha scelto il tool giusto o "Abstain" in modo corretto).
4. **Data Visualization (Matplotlib):**
   - Creare i grafici a barre "Latenza: SystemOne vs Generativo".
   - Creare un grafico a dispersione o a torta "Accuratezza: 4B vs 0.5B".
   - (Questi grafici finiranno direttamente nell'elaborato di tesi).
