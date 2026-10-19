# Fase 14j - Calcolo delle incongruenze

Data: 2026-10-19. Ramo phase-14. Nota integrativa di PHASE_14.md e PHASE_14_REVIEW_MIGRATION.md.

## Ambito

review_plan.py calcola un piano senza accedere al database e senza modificare gli argomenti. Non è ancora collegato alle rotte. Non salva bozze, inventari o revisioni.

Per carta, la pool finale è la disponibilità attuale più la somma, su tutti i piloti, di copie fisicamente possedute meno copie finali richieste. Le copie fisicamente possedute sono total meno consumed; le giocate active non sono ancora state sottratte dall'inventario. Per le righe omesse la destinazione è total meno consumed meno active. Sono controllate tutte le righe, non solo quelle inviate dal browser.

Il saldo è aggregato prima dei controlli: prelievi e restituzioni della stessa carta si compensano senza dipendere dall'ordine dei piloti. Un saldo negativo, un saldo oltre il massimo noto, conteggi fuori dai limiti e dati incoerenti producono problemi raggruppati per carta. Se il massimo è None il limite superiore non è verificato. L'adattatore database dovrà fornire anche le carte con disponibilità zero e le capacità note.

## Verifiche realmente eseguite

Eseguiti 10 test unittest del calcolo puro nell'ambiente Python disponibile: tutti superati. Il sorgente è stato eseguito come modulo in memoria, senza importare l'applicazione del repository. I test coprono carta omessa, compensazione tra piloti, totale comprensivo di bonus, superamento del totale, carta sconosciuta, pool insufficiente, argomenti immutati, giocate incoerenti, duplicati e disponibilità zero mancante.

Non eseguiti: pytest del repository, test SQLite/API, lint o CI. Nessuna migrazione o modifica al database reale.

## Passi successivi

Collegare i dati reali al piano; applicare atomicamente inventari e registro, oppure salvare soltanto la bozza in caso di errore; gestire la scadenza selettiva per carta; collegare le rotte e la nuova interfaccia. Un piano con problemi non deve essere applicato integralmente dalla conferma manuale. SSE e aggiornamento dal vivo dello stato rimangono rinviati.
