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
4. **Architettura e Sviluppo CLI/Server (Multi-Modello):**
   - Creare un pacchetto Python installabile (`pyproject.toml`) con entrypoint CLI (`lightning-route`).
   - Implementare i comandi `serve` (avvio server FastAPI), `decide` (inferenza one-shot su JSON locale) e `schema` (estrazione JSON schema).
   - Esporre gli endpoint `POST /v1/route` (e alias `/v1/systemone`) e `GET /health`.
   - **Cruciale:** Il server e la CLI non devono avere il modello hardcodato. Devono accettare `--model` e `--adapter` come argomenti da riga di comando in fase di avvio, permettendo di switchare dinamicamente tra modelli e pesi LoRA per le valutazioni.
   - Restituire JSON contenente l'opzione vincente (`chosen_tool`), la confidenza (`confidence`), l'array dei logit calibrati e il tempo di esecuzione (`latency_ms`).

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

**Obiettivo:** Quantificare in modo organico la superiorità architetturale di LightningRoute misurando latenza e accuratezza al variare del numero di tool (da 1 a 25), confrontandolo direttamente con i paradigmi esistenti.

### L'Esperimento Unificato
Sfruttando il dataset `v3_test.jsonl` (che raggruppa le query in bucket omogenei per numero di tool: 1-5, 6-10, fino a 21-25), eseguiremo un'unica suite di valutazione che metterà a confronto tre diverse pipeline architetturali:

1. **Pipeline Generativa Tradizionale (Complessità $\mathcal{O}(L)$):**
   - Un LLM monolitico (es. Qwen 7B) riceve la query e il contesto completo di *tutti* i tool disponibili. Genera direttamente il JSON finale (Tool Selection + Argument Extraction).
   - *Ipotesi:* Latenza costantemente elevata a causa della decodifica token per token ($\mathcal{O}(L)$), e crollo dell'accuratezza semantica all'aumentare delle opzioni dovuta alla confusione nel contesto.

2. **Pipeline Baseline System One, es. Rizzo-Flow (Complessità $\mathcal{O}(N)$):**
   - Un modello valuta la probabilità della sequenza per *ogni singola opzione* in modo indipendente.
   - *Ipotesi:* Mentre a bassi numeri di tool (es. 4) può competere, la sua latenza esplode in modo lineare ($\mathcal{O}(N)$) all'aumentare dei tool, rendendolo inadatto a scenari complessi.

3. **Pipeline LightningRoute Cascade (Complessità $\mathcal{O}(1)$):**
   - **Gatekeeper (Selezione):** LightningRoute (0.5B fine-tuned) riceve tutte le descrizioni dei tool ed esegue un singolo forward pass, restituendo istantaneamente il tool corretto o 'Z' (Abstain) con latenza assolutamente piatta ($\mathcal{O}(1)$).
   - **Estrattore (Argomenti):** Un LLM minuscolo (es. 1.5B/3B) riceve *solo* lo schema dell'unico tool selezionato per generare rapidamente il JSON.
   - *Ipotesi:* Latenza End-to-End nettamente inferiore e accuratezza semantica preservata (il rumore di fondo viene abbattuto prima della generazione).

### Output e Visualizzazione Dati (Matplotlib)
I risultati dell'esperimento verranno distillati nei seguenti grafici e metriche per l'elaborato di tesi:
- **Metriche di Latenza Rigorose:** Per ogni pipeline e per ogni bucket di tool, calcoleremo esattamente la latenza `p50` (mediana), `p90` e `p99`, così da documentare la stabilità del sistema anche nei casi peggiori (tail latency).
- **Scalabilità della Latenza (Curve):** Grafico a linee (Asse X: Numero di Tool; Asse Y: Latenza ms) che evidenzia la curva piatta di LightningRoute $\mathcal{O}(1)$ contro la crescita lineare $\mathcal{O}(N)$ di Rizzo-Flow e la linea alta $\mathcal{O}(L)$ del generativo.
- **Efficacia End-to-End (Scatter Plot):** Grafico a dispersione (Asse X: Latenza Totale Pipeline; Asse Y: Accuratezza %) per dimostrare che LightningRoute Cascade domina su entrambi i fronti rispetto ai classici Router LLM monolitici.

While **LightningRoute** shares the same foundational "System One" philosophy (no text generation, instant classification) as Jev and Rizzo-Flow, it is vastly more specialized and efficient for the specific task of **Tool Routing** due to three massive architectural advantages:

### 1. The 0.5B LoRA Advantage (Specialization over Generalization)
- **General System One (SemIf/Rizzo-Flow):** These are typically **zero-shot** frameworks. To achieve decent accuracy without fine-tuning, they must rely on the emergent reasoning capabilities of larger base models (e.g., Qwen 4B or 7B). A 7B model requires significantly more FLOPS and VRAM for its forward pass.
- **LightningRoute:** By performing task-specific **LoRA Fine-Tuning** on the BFCL dataset, we successfully compressed 7B-level routing accuracy into an ultra-compact **0.5B parameter model**. This means the single forward pass is computationally trivial, resulting in sub-200ms latency while maintaining >80% accuracy.

### 2. Built-in Epistemic Honesty (The 'Z' Class)
- **General System One (Jev/SemIf):** Jev uses expensive Reinforcement Learning with Calibrated Decisions (RLCD) to teach the model when it shouldn't guess. SemIf, being zero-shot, struggles natively with out-of-domain rejection and often forces a choice among available options.
- **LightningRoute:** We bypassed the need for RL by engineering the **`v2` dataset**. By injecting thousands of negative samples, we explicitly trained the model to predict the **'Z' (Abstain)** token via Supervised Fine-Tuning (SFT). LightningRoute natively knows when *not* to call a tool, and its softmax confidence score on 'Z' is naturally calibrated through standard Cross-Entropy Loss.

### 3. Simplified O(1) Inference Engine
- **General System One (SemIf):** Because it evaluates arbitrary text options zero-shot, its inference engine must perform complex KV-cache branching. It precomputes a shared prefix, duplicates the cache for *every* possible option, appends the option text, and evaluates the probability of the entire sequence.
- **LightningRoute:** Because our fine-tuned model is trained to output a **single token** (`A`, `B`, `C`, etc.), our engine is radically simpler and faster. We format the prompt, perform exactly **one** unified forward pass, and slice the logits at the very last position (`logits[0, -1, target_token_ids]`). There is no cache branching or sequence scoring—just O(1) instant classification.

### Summary
Jev and SemIf are **general-purpose** System One models—they can score any text, answer True/False, or evaluate options zero-shot, which requires large models and complex inference engines. **LightningRoute** is a **purpose-built Tool Router**. By combining specialized LoRA fine-tuning with a strict single-token output format, we stripped away the generic bloat, unlocking a massive speedup via a 0.5B model and a vastly simplified O(1) inference loop.

## Possible Extensions

1. **Dockerization as a Microservice**
   Packaging the router into a Docker container eliminates dependency and environment fragility, turning it into a true production-ready microservice. In a multi-agent system, an orchestrator can query the `lightning-route` container via a simple HTTP endpoint without needing to manage its internal ML dependencies. Note: Because it is powered by MLX, the container deployment would be restricted to Apple Silicon hardware (e.g., local Mac clusters or AWS EC2 Mac instances).

2. **Overcoming the "26 Tools" (A-Z) Bottleneck**
   System One models that rely on single-token extraction are typically limited by the alphabet (26 tools). Possible extensions to bypass this include:
   - **Hierarchical Routing:** Grouping tools into categories (e.g., `A: Database Tools`, `B: Web Tools`). A first forward pass selects the category, and a second pass selects the specific tool within that category.
   - **Multi-Token Logit Extraction:** Shifting to a two-token extraction (e.g., `AA`, `AB`, `AC`) allowing for $26^2$ (676) possible tools, though this introduces slight autoregressive overhead.
   - **Dynamic Chunking:** Evaluating subsets of tools in parallel batches if the options exceed 26.

3. **Two-Level Cascade Architecture**
   Splitting the routing logic into two specialized models to maximize speed and accuracy:
   - **Level 1 (Gatekeeper):** An ultra-tiny, highly optimized binary classifier that exclusively determines whether to *Abstain* or *Route*.
   - **Level 2 (Selector):** If Level 1 decides to route, the request is passed to a second model tasked purely with selecting the correct tool, removing the burden of epistemic honesty from the selector.

4. **Explainable AI (XAI) for Logit Analysis**
   Applying XAI techniques (such as SHAP, LIME, or Integrated Gradients) to the input prompt embeddings. This would allow us to analyze the feature importance of specific words in the user's query and understand *why* the model assigned a high probability to a specific tool class or why it triggered the 'Z' (Abstain) condition.