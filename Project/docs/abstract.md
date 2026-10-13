# Thesis abstract (v0.4)

> **Status:** v0.4 (2026-10-13). It replaces v0.3.1 (2026-10-08/09). New since v0.3.1: the local-inference chapter and the
> cost argument (reading vs writing on one device), the equal-output judges with probabilities, the control on the
> restricted readout (B2), the energy measurements, a second 0.5B run, the general-purpose decision model d1-3B and the
> decision-model ecosystem. Experiments continue until 2026-10-30; numbers may still change slightly.
> Numbers come from `docs/thesis_notes.md` and `checkpoint_2026-10-10.md`; the thesis summary (`Thesis/content/summary.tex`)
> follows the same content.

---

## English

### Title
**GroundOne: A Specialist System One for Groundedness Verification in Local Retrieval-Augmented Generation**
*Fine-tuning compact language models as single-pass, calibrated verifiers on Apple Silicon*

### Context
Retrieval-augmented generation (RAG) is the standard way to give language models access to private documents, and small
open-weight models now make it possible to run the whole pipeline on the user's own device, with privacy, offline use
and no per-token cost. Retrieval does not remove hallucination: answers still contain sentences that the retrieved
document does not support or that contradict it. A local assistant therefore needs a verifier that checks every answer,
sentence by sentence, on the same constrained machine as the generator. On such a machine reading text is cheap and
writing it is expensive: on the laptop used here, generating a token costs 14–16 times more than reading one, because
decoding is limited by memory bandwidth, and the asymmetry holds on every class of local hardware.

### State of the art
- **Encoder-based checkers** (AlignScore, MiniCheck, HHEM) are small and fast but return one fixed binary score per
  (document, sentence) pair.
- **Generative judges** (LLM-as-a-judge) are flexible but write their verdicts token by token; small judges break the
  output format and their confidence is rarely usable as a probability.
- **System One models**, also called *decision models*, answer closed questions in a single forward pass by reading the
  logits of the answer options (TypeSafe's Jev; open SemIf, Rizzo-Flow; in 2026 also Liquid AI's d1-3B, Cloudflare's Clef
  and about 1,500 models under the Hugging Face `decision-model` tag). The evidence is mostly self-reported and the
  open models are general-purpose.

### Research gap
No controlled, independent study shows whether a compact System One specialised in one task can match generative judges,
dedicated encoders and general-purpose decision models on that task, where its advantage comes from (specialisation, the
way the decision is read, or model size), and whether its probabilities are usable, all within the memory, time and
energy budget of a consumer laptop.

### Approach
**GroundOne** is a System One specialised in one decision: for each sentence of a RAG answer, does the retrieved document
*support* it, *contradict* it or *not mention* it?
- **Single-pass readout.** A marker follows every sentence; the verdicts of all K sentences are read from the logits of
  three letters in one forward pass, with no text generation.
- **Training.** Qwen2.5-0.5B and 3B, fine-tuned with LoRA (MLX, 8-bit) on human-labelled RAGTruth answers, with a
  class-weighted loss restricted to the three letters.
- **Calibration and served output.** Temperature and per-class bias fitted on development data; a threshold chosen on
  the same data turns the probabilities into consistent labels and strict or lenient flags.
- **Fully local.** Data preparation, training, evaluation, serving and every baseline run on one Apple M4 laptop with
  16 GB, with no external service.

### Evaluation
- **Three test sets built and frozen before training:** the RAGTruth test split (three-way, by number of sentences K),
  LLM-AggreFact (binary, comparable with published systems) and VitaminC (three-way, different domain).
- **Comparisons:** cues that never read the document; the untrained models; terse and verbose generative judges of the
  same size, with and without probabilities; the same model deciding by the token it would generate (control B2); two
  general-purpose System One models (Rizzo-Flow 4B, Liquid AI d1-3B); the encoders MiniCheck and HHEM.
- **Measurements:** balanced accuracy and AUROC with cluster-bootstrap intervals; calibration (ECE, reliability,
  risk–coverage); time and energy per answer as a function of K; an analysis of local hardware that bounds what any
  generative verifier must pay on each class of machine.

### Results (13 October 2026)
- **In domain (RAGTruth).** Three-way balanced accuracy 0.769 (0.5B) and 0.832 (3B), against 0.37 and 0.44 untrained;
  AUROC 0.905 and 0.940, above the encoders (about 0.82). GroundOne clearly outperforms Rizzo-Flow (0.603 vs 0.798 for
  the 0.5B on the same answers) and d1-3B (0.657). A second 0.5B run reproduces the result (0.767).
- **External benchmark (LLM-AggreFact).** The 3B reaches 74.8, on par with MiniCheck-RoBERTa (74.0, not significant),
  above the published zero-shot 7B model and below the closed System One Jev measured independently (78.6).
- **Out of domain (VitaminC).** Transfer is weak (0.527); there the general-purpose d1-3B is stronger (0.724).
- **Speed and energy.** For answers of 14 or more sentences GroundOne is about 2× faster than a terse and 6× faster than
  a verbose judge of the same size, with always valid output, and uses less energy (5.5 J per answer with the 0.5B, 33 J
  with the 3B), by a smaller factor than in time.
- **Readout and probabilities.** With the same trained model, reading the three admissible letters is more accurate than
  letting the model generate its verdict (+0.25 balanced accuracy for the 0.5B, +0.07 for the 3B). After calibration the
  ECE on the test set is 0.019, whereas generative judges asked for the same output give probabilities that barely
  separate correct from incorrect decisions.
- **Limits.** Weak transfer outside the RAG domain; hallucinations hidden in sentences that otherwise copy the source are
  detected only in part; training is not fully stable across seeds (one 0.5B run collapsed).

### Contributions
1. **GroundOne**, an open specialist System One for sentence-level groundedness verification that runs entirely on a
   laptop (package, command-line interface, local HTTP API compatible with existing System One clients).
2. **A sentence-level dataset derived from public annotations**, with three test sets checked and frozen before training.
3. **A controlled decomposition of the gains** (specialisation, restricted readout, model size) against a broad set of
   baselines on the same hardware.
4. **A study of calibration, time and energy**, set in an analysis of local inference that bounds, for each class of
   consumer hardware, the cost that a generative verifier must pay and a System One does not.

**Keywords:** System One models, decision models, retrieval-augmented generation, hallucination detection, groundedness
verification, local inference, calibration, LoRA, Apple Silicon, MLX.

---

## Italiano

### Titolo
**GroundOne: un System One specialista per la verifica della groundedness nella RAG locale**
*Fine-tuning di modelli linguistici compatti come verificatori calibrati a singolo passaggio su Apple Silicon*

### Contesto
La retrieval-augmented generation (RAG) è il modo standard di dare ai modelli linguistici accesso a documenti privati, e
i modelli open-weight piccoli permettono oggi di eseguire l'intera pipeline sul dispositivo dell'utente, a vantaggio di
privacy, uso offline e costi. Il recupero dei documenti non elimina però le allucinazioni: le risposte contengono ancora
frasi che il documento recuperato non supporta o che lo contraddicono. Un assistente locale ha quindi bisogno di un
verificatore che controlli ogni risposta, frase per frase, sulla stessa macchina del generatore. Su una macchina di questo
tipo leggere un token costa molto meno che scriverlo: sul laptop usato nella tesi generare un token costa 14–16 volte più
che leggerlo, perché la generazione è limitata dalla banda di memoria, e l'asimmetria vale per ogni classe di hardware
locale.

### Stato dell'arte
- **Verificatori basati su encoder** (AlignScore, MiniCheck, HHEM): piccoli e veloci, ma restituiscono un unico punteggio
  binario per ogni coppia (documento, frase).
- **Giudici generativi** (LLM-as-a-judge): flessibili, ma scrivono i verdetti token per token; i giudici piccoli non
  rispettano il formato e la loro confidenza è raramente utilizzabile come probabilità.
- **Modelli System One**, detti anche *decision model*: rispondono a domande chiuse in un solo forward pass leggendo i
  logit delle opzioni (Jev di TypeSafe; gli open SemIf e Rizzo-Flow; nel 2026 anche d1-3B di Liquid AI, Clef di
  Cloudflare e circa 1500 modelli sotto il tag `decision-model` di Hugging Face). Le evidenze sono per lo più dichiarate
  dagli autori e i modelli aperti sono generalisti.

### Gap di ricerca
Manca uno studio controllato e indipendente che mostri se un System One compatto specializzato in un solo task possa
eguagliare giudici generativi, encoder dedicati e decision model generalisti su quel task, da dove derivi l'eventuale
vantaggio (specializzazione, modo di leggere la decisione o dimensione del modello) e se le sue probabilità siano
utilizzabili, il tutto entro i limiti di memoria, tempo ed energia di un laptop consumer.

### Approccio
**GroundOne** è un System One specializzato in un'unica decisione: per ogni frase di una risposta RAG, il documento
recuperato la *supporta*, la *contraddice* o *non la menziona*?
- **Readout in un solo passaggio.** Un marker segue ogni frase; i verdetti di tutte le K frasi si leggono dai logit di
  tre lettere in un unico forward pass, senza generare testo.
- **Addestramento.** Qwen2.5-0.5B e 3B, con fine-tuning LoRA (MLX, 8 bit) sulle risposte di RAGTruth annotate
  manualmente, con una loss pesata per classe e ristretta alle tre lettere.
- **Calibrazione e output servito.** Temperatura e bias per classe stimati sul dev set; una soglia scelta sugli stessi
  dati traduce le probabilità in etichette coerenti e in segnalazioni strict o lenient.
- **Interamente locale.** Preparazione dei dati, addestramento, valutazione, messa in servizio e tutte le baseline girano
  su un unico laptop Apple M4 da 16 GB, senza servizi esterni.

### Valutazione
- **Tre test set costruiti e congelati prima dell'addestramento:** il test di RAGTruth (tre classi, per numero di frasi
  K), LLM-AggreFact (binario, confrontabile con la letteratura) e VitaminC (tre classi, altro dominio).
- **Confronti:** indizi che non leggono il documento; i modelli non addestrati; giudici generativi sintetici e verbosi
  della stessa dimensione, con e senza probabilità; lo stesso modello che decide in base al token che genererebbe
  (controllo B2); due System One generalisti (Rizzo-Flow 4B, d1-3B di Liquid AI); gli encoder MiniCheck e HHEM.
- **Misure:** balanced accuracy e AUROC con intervalli bootstrap a cluster; calibrazione (ECE, reliability,
  rischio–copertura); tempo ed energia per risposta in funzione di K; un'analisi dell'hardware locale che stabilisce il
  costo minimo di qualunque verificatore generativo su ciascuna classe di macchine.

### Risultati (13 ottobre 2026)
- **Nel dominio (RAGTruth).** Balanced accuracy a tre classi 0.769 (0.5B) e 0.832 (3B), contro 0.37 e 0.44 dei modelli
  non addestrati; AUROC 0.905 e 0.940, sopra gli encoder (circa 0.82). GroundOne supera nettamente Rizzo-Flow (0.603
  contro 0.798 del 0.5B sulle stesse risposte) e d1-3B (0.657). Un secondo addestramento del 0.5B riproduce il risultato
  (0.767).
- **Benchmark esterno (LLM-AggreFact).** Il 3B raggiunge 74.8, alla pari con MiniCheck-RoBERTa (74.0, differenza non
  significativa), sopra il modello 7B zero-shot pubblicato e sotto il System One chiuso Jev misurato in modo indipendente
  (78.6).
- **Fuori dominio (VitaminC).** Il trasferimento è debole (0.527); qui il generalista d1-3B è più forte (0.724).
- **Velocità ed energia.** Per risposte di 14 o più frasi GroundOne è circa 2 volte più veloce di un giudice sintetico e
  6 volte più di uno verboso della stessa dimensione, con output sempre valido, e consuma meno energia (5.5 J per risposta
  con il 0.5B, 33 J con il 3B), con un vantaggio inferiore a quello sul tempo.
- **Readout e probabilità.** Con lo stesso modello addestrato, leggere le tre lettere ammesse è più accurato che lasciar
  generare il verdetto (+0.25 di balanced accuracy per il 0.5B, +0.07 per il 3B). Dopo la calibrazione l'ECE sul test set
  è 0.019, mentre i giudici generativi a cui si chiede lo stesso output forniscono probabilità che distinguono a stento le
  decisioni corrette da quelle errate.
- **Limiti.** Trasferimento debole fuori dal dominio RAG; le allucinazioni nascoste in frasi che per il resto ricalcano
  la fonte vengono individuate solo in parte; l'addestramento non è del tutto stabile al variare del seed (un
  addestramento del 0.5B è collassato).

### Contributi
1. **GroundOne**, un System One specialista e aperto per la verifica della groundedness a livello di frase, eseguito
   interamente su un laptop (pacchetto, interfaccia a riga di comando, API HTTP locale compatibile con i client System One
   esistenti).
2. **Un dataset a livello di frase derivato da annotazioni pubbliche**, con tre test set verificati e congelati prima
   dell'addestramento.
3. **Una scomposizione controllata dei guadagni** (specializzazione, readout ristretto, dimensione del modello) rispetto a
   un ampio insieme di baseline sullo stesso hardware.
4. **Uno studio di calibrazione, tempo ed energia**, inserito in un'analisi dell'inferenza locale che stabilisce, per ogni
   classe di hardware consumer, il costo che un verificatore generativo deve pagare e che un System One non paga.

**Parole chiave:** modelli System One, decision model, retrieval-augmented generation, rilevamento delle allucinazioni,
verifica della groundedness, inferenza locale, calibrazione, LoRA, Apple Silicon, MLX.
