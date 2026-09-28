# Abstract: Accelerare i Sistemi Multi-Agente tramite Architetture System One

## Stato dell'Arte (SOTA)
L'attuale paradigma per i sistemi autonomi multi-agente e i framework di tool-calling (es. LangChain, AutoGPT, Model Context Protocol) si affida pesantemente a standard Large Language Models (LLM) che agiscono come orchestratori decisionali. In questi sistemi, l'agente opera in un ciclo continuo: legge lo stato, determina la prossima azione o strumento da invocare, genera i parametri del tool in formato testuale (JSON) e osserva il risultato.

Pur essendo altamente capace, questo approccio soffre di un grave collo di bottiglia in termini di latenza a causa della **natura autoregressiva degli LLM**. La generazione del payload JSON per la chiamata a un tool richiede un processo di decodifica token per token, portando a tempi di esecuzione che spesso superano diversi secondi per ogni singola decisione di routing. Quando si scala verso workflow complessi che richiedono dozzine di micro-decisioni, questa latenza si accumula, rendendo impraticabile l'esecuzione agentica in tempo reale (o quasi) su hardware consumer, a meno di non sostenere costi proibitivi per le API cloud.

## La Nostra Proposta
Questo progetto di tesi introduce **SemIf-Router**, un orchestratore agentico locale ultra-veloce basato sul nascente paradigma dei modelli *"System One"* (ispirato all'architettura Jev e implementato tramite il framework open-source `SemIf`).

Invece di generare testualmente il JSON del tool da chiamare, SemIf-Router bypassa completamente la decodifica autoregressiva. Il sistema traduce dinamicamente le descrizioni dei tool (API schemas) in *Opzioni Testuali*. Il prompt dell'utente (lo *State*) viene processato una singola volta e memorizzato nella **KV Cache**. Successivamente, il modello valuta tutte le opzioni (i tool disponibili) in parallelo, restituendo istantaneamente una distribuzione di probabilità calibrata.

Sfruttando il backend nativo Apple (MLX) su un MacBook Pro con 16GB di Unified Memory, il progetto dimostra come modelli di taglia ridotta (da 0.5 a 4 miliardi di parametri) possano abbattere la latenza di routing da un ordine di grandezza di secondi (tipico dei server autoregressivi come LM Studio o Llama.cpp) a decine di **millisecondi**.

Il lavoro prevede l'implementazione del router come API locale drop-in replacement, seguita da un rigoroso benchmarking contro modelli generativi standard sul *Berkeley Function Calling Leaderboard (BFCL)*. L'obiettivo principale è dimostrare che l'architettura System One risolve il problema della latenza O(N) legata alla generazione dei token mantenendo una *Recall@1* competitiva. 

Infine, la ricerca indagherà il **trade-off tra Accuratezza e Latenza**, confrontando le performance del modello base (es. Qwen3.5-4B) con una controparte ancora più piccola (es. Qwen2.5-0.5B o MiniCPM-2B), per determinare il limite inferiore dimensionale capace di garantire routing agentico affidabile in locale.
