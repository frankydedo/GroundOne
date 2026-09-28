# Implementation Plan: Custom System One Router (Custom Jev-like Model)

## Obiettivo Principale
Progettare, addestrare e implementare da zero un orchestratore "System One" specializzato nel tool-routing per framework multi-agente. Invece di limitarsi ad applicare soluzioni esistenti (come SemIf zero-shot o Rizzo Flow), il progetto prevede lo sviluppo del framework di inferenza e il fine-tuning dei pesi del modello, il tutto eseguito al 100% in locale su architettura Apple Silicon.

## Modelli e Hardware
- **Hardware:** MacBook Pro Apple Silicon (16GB Unified Memory).
- **Modelli Base (Quantizzati MLX 8-bit):** 
  - [`lmstudio-community/Qwen3.5-4B-MLX-8bit`](https://huggingface.co/lmstudio-community/Qwen3.5-4B-MLX-8bit): Modello principale per stabilire il "tetto" di accuratezza.
  - [`lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit`](https://huggingface.co/lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit): Modello ultra-compatto per analizzare la tenuta dell'accuratezza in dimensioni ridotte e massimizzare la riduzione della latenza.
- **Framework:** `MLX` e `MLX-LM` (nativi Apple). A differenza di LM Studio (che è esclusivamente un motore di inferenza "black-box" visivo), MLX fornisce le API Python necessarie per calcolare i gradienti e modificare i pesi del modello (LoRA Fine-Tuning) sfruttando appieno la GPU integrata del Mac. LM Studio verrà comunque utilizzato per far girare la baseline generativa in fase di benchmarking.

## Dataset
- **Origine:** Berkeley Function Calling Leaderboard (BFCL) o simili.
- **Trasformazione:** Il dataset originale dovrà essere trasformato. I prompt di input diventeranno lo "State", i tool disponibili verranno tradotti in un formato a "Scelta Multipla", e i target di addestramento diventeranno le lettere corrispondenti alle risposte esatte. 

## Metodologia Operativa

Il progetto sarà strutturato in 4 fasi incrementali:

### Fase 1: Preparazione del Dataset "Typed Decisions"
- Acquisizione del dataset BFCL.
- Sviluppo di uno script Python che pre-processa i dati JSON convertendoli nel formato Jev-like (State + Multiple Choice Options).
- Bilanciamento del dataset: inserimento di esempi negativi dove il modello deve imparare a rispondere "Nessun tool adatto" (Abstain) per sviluppare *epistemic honesty*.

### Fase 2: Ingegnerizzazione dell'Inferenza (Router Framework)
- Partendo dai concetti base di `SemIf` (estrazione selettiva dei logit e caching della KV per prompt condivisi), verrà sviluppato il motore di inferenza custom in Python/MLX.
- Realizzazione di un wrapper API (es. tramite FastAPI) che simula le chiamate `POST /v1/systemone`.

### Fase 3: LoRA Fine-Tuning in Locale (Multi-Modello)
- **SFT vs RLCD:** A causa dei vincoli di tempo e hardware (MacBook Pro), il progetto non implementerà un costoso ciclo di Reinforcement Learning for Calibrated Decisions (RLCD). Verrà invece eseguito un **Supervised Fine-Tuning (SFT)** tramite architettura LoRA usando `MLX-LM`.
- **Simulazione della Calibrazione:** Gli effetti dell'RLCD (ovvero l'onestà epistemica) verranno approssimati tramite la cura del dataset. Grazie ai dati negativi (Abstain) inseriti nella Fase 1 e all'ottimizzazione della _Cross-Entropy Loss_ sugli errori di predizione, il modello imparerà a calibrare le proprie confidenze senza bisogno di Reinforcement Learning.
- Il modello non imparerà a generare testo, ma ottimizzerà la sua Loss esclusivamente sull'ultimo token (la lettera della risposta esatta). 
- **Effort per due modelli:** Bassissimo. Una volta scritta la pipeline di training sui dati, addestrare un secondo modello più piccolo richiederà unicamente di cambiare il parametro del percorso del modello e attendere che finisca.

### Fase 4: Benchmarking e Risultati (Confronto Baseline)
- **Confronto Generativo vs System One:** Test dell'architettura classica (LLM Generativo interrogato via LM Studio in JSON) contro il nostro router System One, per dimostrare l'annullamento della latenza legata all'autoregressione.
- **Confronto Dimensionale (Trade-off):** Confronto incrociato tra il nostro router a 4B parametri e quello a 0.5B/1.5B per mappare esattamente quanto si perde in accuratezza (Recall@1) a fronte di un guadagno estremo in velocità.

## Analisi di Feasibility ed Effort
- **Infrastruttura:** Pienamente fattibile. L'ecosistema MLX consente il training LoRA di un modello 4B all'interno di 16GB di Unified Memory.
- **Tempistiche (stima 2-3 mesi):**
  - *Fase 1 (Dati):* 1-2 settimane.
  - *Fase 2 (Ingegneria):* 1-2 settimane.
  - *Fase 3 (Addestramento 0.5B e 4B):* 2-3 settimane.
  - *Fase 4 (Benchmark contro Baseline):* 1-2 settimane.
- **Valore Accademico:** Molto elevato. Passaggio da un progetto analitico a un lavoro di _Machine Learning Engineering_ end-to-end.
