# Fase 14j - Revisione guidata nell'interfaccia

Aggiornamento: 2026-10-19. Ramo phase-14. Per l'esito complessivo verificato e l'indice delle note vedere PHASE_14_VALIDATION.md.

## Interfaccia attuale

race-review-panel.svelte usa il nuovo ReviewCountsStore e sostituisce nella revisione elenco giocate e modulo bonus/rimozioni con inventari sponsor. Ogni pilota ha un pannello a scomparsa; il primo nasce aperto. Ogni carta mostra immagine, rimaste/totali, partenza e bonus S. + e − modificano soltanto la bozza entro 0..totale.

Prossimo salva sul server tutti i conteggi e marca il pilota; Indietro e cambio pannello salvano senza aggiungere la spunta. Sull'ultimo pilota Completa controllo chiude il pannello. La conferma si abilita solo dopo tutte le spunte. Cambiare una carta revoca la spunta del pilota. In caso di 409 il popup elenca carte, ragioni e quantità della pool senza cancellare la bozza.

## Recupero e scadenza

I conteggi si recuperano dalla bozza server; sessionStorage conserva anche modifiche e spunte della scheda per la specifica revisione e titolare. Le spunte non sono salvate nel database né imposte dal backend. Se sessionStorage non è disponibile lo schermo avvisa; restano recuperabili i conteggi salvati con la navigazione. Le modifiche locali non ancora inviate non vengono applicate dal server alla scadenza. Una bozza fuori dai limiti non viene troncata silenziosamente: si mostra un avviso e si riparte dall'inventario corrente per ricontrollare.

Il timer non genera polling continuo: alla scadenza legge una volta lo stato, attivando la chiusura sul server; su errore è disponibile Aggiorna stato. Dopo conferma, riapertura e rinuncia viene ricaricata la pagina per aggiornare anche intestazione e permessi caricati in onMount. Non è sincronizzazione tra dispositivi: SSE resta rinviato.

## Verifiche

Tre test Vitest aggiunti per merge immutabile, quantità fuori limite e pilota assente. L'assistente non ha eseguito localmente Vitest, lint, type-check, build o test del nuovo store/UI.

Il 2026-10-19 l'assistente ha verificato su GitHub il run 39215475748 della PR #13, riferito alla testa da48921f100a0053881b76e0984093ea100d8568: frontend (check, lint, test, build), backend pytest e migrazioni risultano tutti success. Le precedenti segnalazioni Prettier sono quindi superate su quella testa. Non si dichiarano eseguiti test browser end-to-end né una copertura aggiuntiva non presente nei check.

L'autore ha confermato alle 09:28 CEST che ora funziona e alle 09:33 CEST ha riferito una prova complessivamente positiva. Non ha specificato un elenco dei casi provati, quindi questa nota non attribuisce esiti puntuali a permessi, scadenza, recupero tra schede, mobile, popup o concorrenza.

## Stato del ramo

PR #13 ancora aperta, in bozza e non unita a main al momento della verifica. Nessuna migrazione aggiunta o applicata da questo aggiornamento documentale. Il vecchio store e le vecchie rotte restano per compatibilità. L'implementazione è presente e ha CI verde sulla testa verificata, ma non è dichiarata collaudata esaustivamente end-to-end.
