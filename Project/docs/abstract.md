# Thesis abstract (draft v0.3)

> **Status:** v0.3 (2026-10-08). It replaces v0.2 (2026-10-05) after the task was redefined (one three-way decision per sentence, D20), the dataset was rebuilt (D21) and the first complete round of experiments ran.
> It includes **preliminary results** (0.5B and 3B, frozen test sets). Pending: T2 for the 3B, confidence intervals, the demo.
> The thesis summary in `Thesis/content/summary.tex` follows this text; the numbers come from `docs/thesis_notes.md`.
> Working system name: **GroundOne**.

---

## English

### Title
**A Specialist System One for Local RAG: Fine-Tuning Compact Language Models as Single-Pass, Calibrated Groundedness Verifiers on Apple Silicon**

### Context
Retrieval-augmented generation (RAG) is the standard way to give language models access to private documents, and running the whole pipeline on the user's own device is now practical on consumer hardware. Retrieval does not remove hallucination, however: generated answers still contain sentences that the retrieved context does not support. Detecting them is a prerequisite for trustworthy local assistants, and the check must run on every answer, on the same constrained machine as the generator.

### State of the art
- **Encoder-based checkers** such as AlignScore, MiniCheck and HHEM are small and fast. They return one fixed score per (document, sentence) pair and score sentences in isolation.
- **LLM-as-a-judge** approaches such as RAGAS, ARES and Lynx are flexible but autoregressive. Their cost grows with the length of the generated verdicts, small models often break the output format, and the confidence they express is rarely calibrated.
- **System One models** (the proprietary Jev; the open SemIf and Rizzo-Flow) answer closed questions in a single forward pass by reading answer-option logits. Evidence for them is mostly vendor-reported, and the open implementations are general-purpose.

### Research gap
No independent, controlled study shows whether a **compact System One specialised in a single task** can match larger generative judges and dedicated encoders on that task, where its advantage comes from, and whether its probabilities are usable, all under the memory and latency limits of a 16 GB laptop.

### Approach
This thesis designs, trains and evaluates **GroundOne**, a System One specialised in one decision: for each sentence of an answer, is it *supported*, *contradicted* or *not mentioned* by the retrieved context?
- **Readout.** The answer is written with a marker after each sentence, and the verdicts for all K sentences are read from the logits of three letters in **one forward pass**, with no text generation.
- **Derived outputs.** A binary groundedness score and a strict or lenient notion of error follow from the three probabilities, so the user chooses the policy without retraining.
- **Training.** Qwen2.5-0.5B and 3B are fine-tuned with LoRA on the human-labelled answers of RAGTruth, using a class-weighted loss restricted to the three letters.
- **Calibration.** A post-hoc temperature and bias are fitted on a development set.

Everything runs on MLX on an Apple M4 laptop with 16 GB.

### Evaluation
- **Three test sets**, built, checked and frozen before training:
  - the RAGTruth test split, with three-way sentence labels and results by number of decisions K;
  - LLM-AggreFact, binary and comparable with published systems;
  - VitaminC, a balanced three-way test from a different domain.
- **Baselines**:
  - cues that never verify the sentence against the document (word overlap, sentence wording);
  - the untrained models;
  - terse and verbose generative judges of the same size;
  - a general-purpose System One (Rizzo-Flow 4B);
  - the encoders MiniCheck-RoBERTa and HHEM.
- **Metrics**: base-rate-independent accuracy, calibration (ECE, Brier, NLL, risk–coverage), and latency per answer as a function of K.

### Preliminary results
- **RAG test set.** Three-way balanced accuracy 0.769 (0.5B) and 0.832 (3B); AUROC 0.905 and 0.940, against 0.737 for word overlap and about 0.82 for the encoders.
  - On the same answers the 0.5B specialist beats the 4B general-purpose System One (0.80 vs 0.60 three-way).
  - Accuracy holds for long answers (0.84 for the 3B with 14 or more sentences).
- **Latency.** At K ≥ 14 GroundOne verifies an answer about 2× faster than a terse and about 6× faster than a verbose generative judge of the same size (0.41 s vs 0.80 s and 2.51 s on the 0.5B). The small judges also often break the output format.
- **Calibration.** Temperature + bias bring the binary ECE on the RAG test set to 0.019.
- **Limits.**
  - Contradictions outside data-to-text are learned only in part.
  - Sentences that copy the source but alter a detail are the main blind spot.
  - Transfer to a different domain (VitaminC) is weak, and there the 3B gains from size rather than from the RAG training.

### Expected contributions
1. An open, reproducible specialist System One for local RAG verification on Apple Silicon (package, CLI, HTTP API).
2. A task-driven dataset with frozen, independently validated test sets.
3. A controlled decomposition of the gains (specialisation, single-pass readout, model size), including the comparison with encoders and a general-purpose System One.
4. An assessment of calibration and selective prediction, and of where the approach fails.

**Keywords:** System One models, retrieval-augmented generation, hallucination detection, groundedness verification, LoRA, calibration, on-device inference, Apple Silicon, MLX.

---

## Italiano

### Titolo
**Un System One specialista per la RAG locale: fine-tuning di modelli linguistici compatti come verificatori di groundedness a singolo passaggio e con probabilità calibrate su Apple Silicon**

### Contesto
La retrieval-augmented generation (RAG) è il modo standard di dare ai modelli linguistici accesso a documenti privati, e far girare l'intera pipeline sul dispositivo dell'utente è oggi realistico. Il recupero dei documenti però non elimina le allucinazioni: le risposte contengono ancora frasi che il contesto non supporta. Individuarle è un requisito per assistenti locali affidabili, e il controllo deve girare a ogni risposta, sulla stessa macchina del generatore.

### Stato dell'arte
- **Encoder**: AlignScore, MiniCheck e HHEM sono piccoli e veloci, ma danno un punteggio fisso per coppia (documento, frase) e valutano le frasi isolate.
- **LLM-as-a-judge**: RAGAS, ARES e Lynx sono flessibili ma autoregressivi. Il costo cresce con la lunghezza dei verdetti generati, i modelli piccoli spesso non rispettano il formato e la confidenza è raramente calibrata.
- **Modelli System One** (Jev; gli open SemIf e Rizzo-Flow): rispondono a domande chiuse in un solo passaggio leggendo i logit delle opzioni, ma le prove sono soprattutto dei produttori e le implementazioni open sono generaliste.

### Gap di ricerca
Manca uno studio indipendente e controllato che mostri se un **System One compatto specializzato in un solo compito** possa eguagliare giudici generativi più grandi ed encoder dedicati, da dove venga il suo vantaggio e se le sue probabilità siano utilizzabili, entro i limiti di memoria e latenza di un laptop da 16 GB.

### Approccio
La tesi progetta, addestra e valuta **GroundOne**, un System One specializzato in una sola decisione: per ogni frase di una risposta, il contesto recuperato la *supporta*, la *contraddice* o *non la menziona*?
- **Lettura.** La risposta è scritta con un marcatore dopo ogni frase, e i verdetti di tutte le K frasi si leggono dai logit di tre lettere in **un solo passaggio**, senza generare testo.
- **Uscite derivate.** Un punteggio binario e una nozione di errore stretta o permissiva derivano dalle tre probabilità, quindi l'utente sceglie la regola senza riaddestrare.
- **Training.** Qwen2.5-0.5B e 3B sono addestrati con LoRA sulle risposte etichettate di RAGTruth, con una loss pesata per classe e ristretta alle tre lettere.
- **Calibrazione.** Temperatura e bias stimati a posteriori sul dev.

Tutto gira su MLX, su un laptop Apple M4 da 16 GB.

### Valutazione
- **Tre test**, costruiti, controllati e congelati prima del training:
  - il test di RAGTruth, a tre classi, con risultati per numero di decisioni K;
  - LLM-AggreFact, binario e confrontabile con la letteratura;
  - VitaminC, bilanciato a tre classi e di un altro dominio.
- **Baseline**:
  - indizi che non verificano la frase sul documento (sovrapposizione di parole, formulazione della frase);
  - i modelli non addestrati;
  - giudici generativi sintetici e verbosi della stessa taglia;
  - un System One generalista (Rizzo-Flow 4B);
  - gli encoder MiniCheck-RoBERTa e HHEM.
- **Metriche**: accuratezza indipendente dalla frequenza delle classi, calibrazione (ECE, Brier, NLL, rischio–copertura) e latenza per risposta in funzione di K.

### Risultati preliminari
- **Test RAG.** Accuratezza bilanciata a tre classi 0.769 (0.5B) e 0.832 (3B); AUROC 0.905 e 0.940, contro 0.737 della sovrapposizione di parole e circa 0.82 degli encoder.
  - Sulle stesse risposte lo specialista da 0.5B batte il System One generalista da 4B (0.80 contro 0.60 a tre classi).
  - L'accuratezza regge sulle risposte lunghe (0.84 per il 3B con 14 o più frasi).
- **Latenza.** Con K ≥ 14 GroundOne verifica una risposta circa 2 volte più velocemente di un giudice generativo sintetico e circa 6 volte più di uno verboso della stessa taglia (0.41 s contro 0.80 s e 2.51 s con il 0.5B). I giudici piccoli inoltre spesso non rispettano il formato.
- **Calibrazione.** Temperatura e bias portano l'ECE binario sul test RAG a 0.019.
- **Limiti.**
  - Le contraddizioni fuori dal data-to-text sono apprese solo in parte.
  - Le frasi che copiano la fonte alterandone un dettaglio sono il principale punto cieco.
  - Il trasferimento a un altro dominio (VitaminC) è debole, e lì il 3B migliora per la dimensione e non per il training RAG.

### Contributi attesi
1. Un System One specialista, open e riproducibile, per la verifica locale nella RAG su Apple Silicon (pacchetto, CLI, API HTTP).
2. Un dataset costruito a partire dal compito, con test congelati e validati in modo indipendente.
3. Una scomposizione controllata dei guadagni (specializzazione, lettura a singolo passaggio, dimensione del modello), con il confronto con encoder e con un System One generalista.
4. Una valutazione della calibrazione, della selective prediction e dei casi in cui l'approccio fallisce.

**Parole chiave:** modelli System One, retrieval-augmented generation, rilevamento di allucinazioni, verifica di groundedness, LoRA, calibrazione, inferenza on-device, Apple Silicon, MLX.
