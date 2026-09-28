# Abstract: Ingegnerizzazione e Fine-Tuning di un Router System One Locale per Sistemi Multi-Agente

## Stato dell'Arte (SOTA)
L'attuale paradigma per i sistemi autonomi multi-agente si affida pesantemente a Large Language Models (LLM) standard che agiscono come orchestratori decisionali. La generazione del payload JSON per la chiamata a un tool richiede un processo di decodifica autoregressiva token per token. Questo meccanismo introduce un grave collo di bottiglia in termini di latenza, rendendo l'esecuzione agentica in tempo reale impraticabile su hardware consumer locale.
Inoltre, i modelli generativi tendono a essere sovra-confidenti e faticano a gestire scenari in cui nessuno strumento a disposizione è adatto (fenomeno delle allucinazioni degli schemi).

## La Nostra Proposta
Questo progetto di tesi introduce un framework e un modello decisionale customizzato, ispirato al nascente paradigma dei modelli *"System One"*. Piuttosto che affidarsi a soluzioni zero-shot pre-esistenti, il lavoro si focalizza sull'intera pipeline di Machine Learning Engineering per costruire un orchestratore agentico ultra-veloce da zero, eseguito al 100% in locale su architettura Apple Silicon.

Invece di generare testo, il router traduce dinamicamente gli schemi dei tool in *Opzioni Testuali*. Sfruttando la KV Cache del framework MLX, lo "State" (prompt utente) viene processato una sola volta, calcolando in parallelo le probabilità delle singole opzioni. 
Il contributo centrale del lavoro è il **LoRA Fine-Tuning** di un LLM compatto (es. Qwen3.5-4B). Il modello viene addestrato specificamente su dati derivati dal *Berkeley Function Calling Leaderboard (BFCL)* per ottimizzare la selezione dei tool e calibrare l'incertezza, insegnando al sistema l'astensione (Abstain) quando le prove sono insufficienti, garantendo così "onestà epistemica".

Il progetto dimostrerà come il combinato tra parallelizzazione in inferenza e fine-tuning specifico per le "Typed Decisions" permetta di abbattere la latenza di routing da secondi a decine di millisecondi, superando i limiti operativi dei tradizionali sistemi generativi pur rimanendo all'interno dei vincoli di memoria di un computer consumer.
