# Fase 16 - Formattazione e contratto del riallineamento

Aggiornamento: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory.
Sorgente generale: PHASE_16_ADMIN_SAVE_API.md. Nessun merge.

## Cronologia delle correzioni

2cf25fd separa pubblicazione dello stile e controlli successivi. ceb12b1 formatta
la bozza UI; 788e6f5 aggiunge l'eccezione ESLint limitata al goto della URL gia'
ricevuta da SvelteKit, senza modificare codice eseguibile o regola globale.
Successivamente f95c915 formatta il test del client PUT, ad377d4 il piano e
7d449cb i quattro componenti del salvataggio UI.

La CI 40012639610 su 7d449cb ha frontend, backend e migrazioni riusciti, ma il
job docs fallito. La causa documentale e' la rinomina del titolo in Salvataggio
admin atomico e bozza UI mentre il workflow richiedeva il titolo originale.
Questa correzione ripristina esattamente # Fase 16 - Salvataggio admin atomico.
La riga di PROJECT_STATUS non usa piu' lo stato fisso del commit 4514348:
viene ricavata da una riga Stato sintetico fase 16 unica, non vuota e senza pipe.
I marcatori restano controllati, anche quando invertiti e adiacenti.

## Verifiche e limiti

Sette test Python del codice di trasformazione su dieci fixture temporanee
riusciti, incluse idempotenza, conservazione testo e assenza di scritture
parziali su errore. Non eseguiti localmente workflow completo, pip, pytest o push.
Il workflow conserva i test mirati esistenti e le protezioni di ramo e percorsi.
Il formatter resta limitato ai quattro componenti di salvataggio, con Prettier
dal lockfile e controlli completi successivi. Nessuna modifica a formatter,
CI ordinaria, dipendenze o codice applicativo in questa correzione.
Propagazione e nuova esecuzione documentale ancora da verificare; nessuna
attesa di nuovi test applicativi per i soli docs. Browser e live non completati.
