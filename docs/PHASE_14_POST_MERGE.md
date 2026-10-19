# Fase 14 - Stato dopo il merge e formattazione campionati

Data: 2026-10-19. Destinazione di questo aggiornamento: main.

## Merge osservato

La PR #13 risulta chiusa e merged alle 12:18:42 UTC (14:18:42 CEST), con merged_by ale3000ale. main osservato dopo il merge: aae6c33ff369257ec84a3fb319574c46625dcb65. La testa della PR era 3d7b1124f77f0b24d6f0145236fa03f99f0349cb. L'assistente ha verificato questi dati tramite GitHub; non attribuisce a sé un'esecuzione del merge non presente nei propri risultati di strumenti.

Le note che descrivono la PR come aperta o in bozza sono storiche e si riferiscono alla situazione precedente al merge. I check della testa della PR restano success; non sono una garanzia sull'esito di ogni successivo run su main.

## Nuova segnalazione

L'autore ha riportato npm run lint fallito su Prettier per championship-groups.spec.ts e routes/championships/+page.svelte. ESLint non è stato raggiunto. Il run preciso del log non è stato identificato, quindi non viene inventato un collegamento tra quel log e uno specifico check della PR.

Il workflow format-championships.yml è limitato a main e viene avviato solo quando cambia il proprio file. Usa npm ci e Prettier del lockfile per i due file segnalati. Pubblica un commit automatico solo se la formattazione li modifica; non forza il push e si arresta se main è avanzato. Il commit automatico non modifica il file del workflow, evitando cicli di attivazione.

Dopo l'eventuale pubblicazione esegue check, lint, test e build. La correzione viene pubblicata prima dei controlli completi. L'esito deve essere letto dopo il run; questo documento non dichiara la correzione già riuscita. Il push del bot non è considerato una garanzia di riavvio della CI ordinaria: il workflow svolge i controlli frontend autonomamente.

Questa automazione richiede contents: write; se policy o protezioni di main vietano il push, l'operazione fallisce esplicitamente senza forzature. La sua rimozione richiede un aggiornamento separato.

Nessuna modifica intenzionale alla logica del gioco, alle dipendenze o al database. Nessuna migrazione locale o backup eseguiti. L'indice e i limiti applicativi restano in PHASE_14_VALIDATION.md; lo stato del merge viene aggiornato da questa nota.
