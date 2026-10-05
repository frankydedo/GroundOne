# Thesis Abstract (draft v0.2)

> **Status:** v0.2 (2026-10-05), revised after the feasibility tests (Phase 0/0b, `phase0_report.md`). It states the problem, the gap and the hypotheses.
> It contains **no final results**; the numbers will be added when the main experiment is done.
> The working system name **GroundOne** is a placeholder.

---

## English

### Title
**A Specialist System One for Local RAG: Fine-Tuning Compact Language Models as Single-Pass, Calibrated Groundedness Verifiers on Apple Silicon**

### Context
Retrieval-Augmented Generation (RAG) is the standard way to ground language models in private documents, and running the whole pipeline on-device (for privacy, offline use and cost) is now practical on consumer hardware. Retrieval, however, does not remove hallucination: generated answers still contain claims that the retrieved context does not support. Detecting these unfaithful claims at generation time is a prerequisite for trustworthy local assistants, and the check has to run on the same constrained machine as the generator, on every answer.

### State of the art
Automatic faithfulness verification currently follows two paradigms. *Encoder-based checkers* (NLI and fact-verification models such as AlignScore, MiniCheck and HHEM) are small and fast, but they are fixed-function classifiers with limited context windows and no way to take instructions or policy in natural language. *LLM-as-a-judge* approaches (e.g. RAGAS, ARES, Lynx) are flexible, but they are autoregressive: the verdict is generated token by token, latency and cost grow with the length of the output, small models often fail to respect the output format, and the confidence they express is rarely well calibrated. A third family has recently emerged: **"System One" models** (the proprietary Jev, and the open re-implementations SemIf and Rizzo-Flow). They answer closed-form questions with a single forward pass, reading the probabilities of the answer options directly from the logits instead of generating text. Evidence for their advantage is mostly vendor-reported or small-scale, and the open implementations are general-purpose.

### Research gap
To the best of our knowledge, there is no independent, controlled study of (i) whether a **task-specialised, fine-tuned compact System One** can match the accuracy of larger generative judges and of dedicated verification encoders on a real task, (ii) how much of its advantage comes from specialisation, how much from the single-pass readout, and how much from the shared-prefix evaluation of several claims over one context, and (iii) whether it delivers usable calibrated probabilities, all **under the memory and latency constraints of consumer hardware** (16 GB unified memory). The comparison with a same-size LLM that emits a single answer token is rarely made, although it is the fair control.

### Proposed solution
We design, train and evaluate **GroundOne**, a System One specialised in *one* task: deciding whether each sentence of an answer is supported by the retrieved context. Compact open models (Qwen2.5 0.5B and 3B) are fine-tuned with LoRA on public, human-labelled faithfulness data, using a training loss restricted to the answer-option logits. At inference the context and the answer are encoded **once** into a KV cache, and all the questions about all the answer sentences (is it supported? is it contradicted? is it acceptable under a given verification rule?) are scored **in parallel** in a single batched pass. The probability of each answer is read directly from the logits, with no text generation, no output parsing and a post-hoc temperature calibration. Besides the plain supported/unsupported decision, GroundOne is trained to answer a three-way question and to follow verification rules written in the prompt, which a fixed-function encoder cannot do. The model is implemented on MLX, runs entirely on a 16 GB Apple Silicon laptop, and is integrated in an end-to-end local RAG demo that flags unsupported sentences in real time.

### Methodology and evaluation
The system is evaluated on public benchmarks with human labels (LLM-AggreFact, RAGTruth), with strict train/test separation and automated leakage checks. The three-way question and the verification rules are evaluated on ANLI and RAGTruth, whose labels distinguish contradicted from unmentioned content. The system is compared against a ladder of baselines that isolates each source of gain: (1) terse and verbose generative LLM judges of the same size, and published results of larger models, (2) the same models with single-token readout but no fine-tuning, (3) a general-purpose System One (Rizzo-Flow), and (4) specialised verification encoders (MiniCheck, HHEM). Latency is measured as a function of the number of decisions per context. Metrics cover discrimination (balanced accuracy, AUROC), calibration (ECE, Brier score, selective-prediction curves), latency (p50/p90/p99 per answer, throughput), peak memory and output-format failure rate. All claims are stated as falsifiable hypotheses; negative results will be reported.

### Expected contributions
1. A reproducible, open implementation of a specialist System One for local RAG verification on Apple Silicon.
2. A controlled decomposition of where a System One gains over an LLM judge (parallel decisions over a shared context, format reliability, specialisation) and where it does not (few decisions, long contexts), including the comparison with dedicated encoders.
3. Evidence on whether a fine-tuned compact System One can follow verification rules given in the prompt, a capability that fixed-function encoders lack.
4. An empirical assessment of the calibration of fine-tuned compact models and of its practical use (confidence thresholds, selective prediction).
5. A working local demo showing the added cost of verification relative to generation.

**Keywords:** System One models, retrieval-augmented generation, hallucination detection, groundedness verification, LoRA fine-tuning, calibration, on-device inference, Apple Silicon, MLX.

---

## Italiano

### Titolo
**Un System One specialista per la RAG locale: fine-tuning di modelli linguistici compatti come verificatori di groundedness a singolo passaggio e con probabilità calibrate su Apple Silicon**

### Contesto
La Retrieval-Augmented Generation (RAG) è il metodo standard per ancorare i modelli linguistici a documenti privati, e farla girare interamente sul dispositivo (per privacy, uso offline e costi) è oggi realistico su hardware consumer. Il recupero dei documenti, però, non elimina le allucinazioni: le risposte generate contengono ancora affermazioni che il contesto recuperato non supporta. Individuarle mentre la risposta viene generata è un requisito per assistenti locali affidabili, e il controllo deve girare sulla stessa macchina vincolata del generatore, a ogni risposta.

### Stato dell'arte
La verifica automatica di fedeltà segue oggi due paradigmi. I *checker basati su encoder* (modelli NLI e di fact-verification come AlignScore, MiniCheck e HHEM) sono piccoli e veloci, ma sono classificatori a funzione fissa, con finestre di contesto limitate e senza la possibilità di ricevere istruzioni o policy in linguaggio naturale. Gli approcci *LLM-as-a-judge* (ad esempio RAGAS, ARES, Lynx) sono flessibili, ma sono autoregressivi: il verdetto viene generato token dopo token, latenza e costo crescono con la lunghezza dell'output, i modelli piccoli spesso non rispettano il formato richiesto e la confidenza che esprimono è raramente ben calibrata. È emersa di recente una terza famiglia: i modelli **"System One"** (il proprietario Jev e le reimplementazioni open SemIf e Rizzo-Flow). Rispondono a domande a risposta chiusa con un solo forward pass, leggendo dai logit le probabilità delle opzioni invece di generare testo. Le prove del loro vantaggio sono perlopiù dichiarate dai produttori o su piccola scala, e le implementazioni open sono general-purpose.

### Gap di ricerca
Per quanto ci risulta, manca uno studio indipendente e controllato che chiarisca (i) se un **System One compatto, specializzato e fine-tuned** possa eguagliare l'accuratezza di giudici generativi più grandi e di encoder di verifica dedicati su un compito reale, (ii) quanto del suo vantaggio derivi dalla specializzazione, quanto dalla lettura a singolo passaggio e quanto dalla valutazione di più affermazioni su un contesto condiviso, e (iii) se fornisca probabilità calibrate utilizzabili, il tutto **entro i vincoli di memoria e latenza di un hardware consumer** (16 GB di memoria unificata). Il confronto con un LLM della stessa taglia che emette un solo token di risposta è raramente svolto, pur essendo il controllo corretto.

### Soluzione proposta
Progettiamo, addestriamo e valutiamo **GroundOne**, un System One specializzato in *un solo* compito: decidere se ciascuna frase di una risposta è supportata dal contesto recuperato. Modelli open compatti (Qwen2.5 0.5B e 3B) vengono addestrati con LoRA su dati pubblici di fedeltà con etichette umane, con una loss ristretta ai logit delle opzioni di risposta. In inferenza, contesto e risposta vengono codificati **una sola volta** in una KV cache, e tutte le domande su tutte le frasi della risposta (è supportata? è contraddetta? è accettabile secondo una data regola di verifica?) vengono valutate **in parallelo** in un unico passaggio. La probabilità di ciascuna risposta è letta direttamente dai logit, senza generazione di testo, senza parsing dell'output e con una calibrazione a posteriori della temperatura. Oltre alla decisione supportata/non supportata, GroundOne è addestrato a rispondere a una domanda a tre valori e a seguire regole di verifica scritte nel prompt, cosa che un encoder a funzione fissa non può fare. Il sistema è implementato su MLX, gira interamente su un laptop Apple Silicon da 16 GB ed è integrato in una demo RAG locale end-to-end che segnala in tempo reale le frasi non supportate.

### Metodologia e valutazione
Il sistema è valutato su benchmark pubblici con etichette umane (LLM-AggreFact, RAGTruth), con separazione rigorosa tra training e test e controlli automatici di contaminazione. La domanda a tre valori e le regole di verifica sono valutate su ANLI e RAGTruth, le cui etichette distinguono il contenuto contraddetto da quello non menzionato. Il confronto avviene con una scala di baseline che isola ciascuna fonte di guadagno: (1) giudici LLM generativi sintetici e verbosi della stessa taglia, e risultati pubblicati di modelli più grandi, (2) gli stessi modelli con lettura a token singolo ma senza fine-tuning, (3) un System One general-purpose (Rizzo-Flow), (4) encoder di verifica specializzati (MiniCheck, HHEM). La latenza è misurata in funzione del numero di decisioni per contesto. Le metriche coprono discriminazione (balanced accuracy, AUROC), calibrazione (ECE, Brier score, curve di selective prediction), latenza (p50/p90/p99 per risposta, throughput), memoria di picco e tasso di errori di formato. Ogni affermazione è formulata come ipotesi falsificabile e i risultati negativi saranno riportati.

### Contributi attesi
1. Un'implementazione aperta e riproducibile di un System One specialista per la verifica nella RAG locale su Apple Silicon.
2. Una scomposizione controllata di dove un System One guadagna rispetto a un giudice LLM (decisioni in parallelo su un contesto condiviso, affidabilità del formato, specializzazione) e dove no (poche decisioni, contesti lunghi), incluso il confronto con encoder dedicati.
3. Evidenza sulla capacità di un System One compatto e fine-tuned di seguire regole di verifica date nel prompt, capacità che gli encoder a funzione fissa non hanno.
4. Una valutazione empirica della calibrazione di modelli compatti fine-tuned e del suo uso pratico (soglie di confidenza, selective prediction).
5. Una demo locale funzionante che mostra il costo aggiunto dalla verifica rispetto alla generazione.

**Parole chiave:** modelli System One, retrieval-augmented generation, rilevamento delle allucinazioni, verifica di groundedness, fine-tuning LoRA, calibrazione, inferenza on-device, Apple Silicon, MLX.
