# Fase 14j - Revisione guidata nell'interfaccia

Data: 2026-10-19. Ramo phase-14. Aggiorna le note precedenti che indicavano il pannello come non ancora collegato.

race-review-panel.svelte usa il nuovo ReviewCountsStore e sostituisce nella revisione elenco giocate e modulo bonus/rimozioni con inventari sponsor. Ogni pilota ha un pannello a scomparsa; il primo nasce aperto. Ogni carta mostra immagine, rimaste/totali, partenza e bonus S. + e − modificano soltanto la bozza entro 0..totale.

Prossimo salva sul server tutti i conteggi e marca il pilota; Indietro e cambio pannello salvano senza aggiungere la spunta. Sull'ultimo pilota Completa controllo chiude il pannello. La conferma si abilita solo dopo tutte le spunte. Cambiare una carta revoca la spunta del pilota. In caso di 409 il popup elenca carte, ragioni e quantità della pool senza cancellare la bozza.

I conteggi si recuperano dalla bozza server; sessionStorage conserva anche modifiche e spunte della scheda per la specifica revisione e titolare. Le spunte non sono salvate nel database né imposte dal backend. Se sessionStorage non è disponibile lo schermo avvisa; restano recuperabili i conteggi salvati con la navigazione. Le modifiche locali non ancora inviate non vengono applicate dal server alla scadenza. Una bozza fuori dai limiti non viene troncata silenziosamente: si mostra un avviso e si riparte dall'inventario corrente per ricontrollare.

Il timer non genera polling continuo: alla scadenza legge una volta lo stato, attivando la chiusura sul server; su errore è disponibile Aggiorna stato. Dopo conferma, riapertura e rinuncia viene ricaricata la pagina per aggiornare anche intestazione e permessi caricati in onMount. Non è sincronizzazione tra dispositivi: SSE resta rinviato.

Tre test Vitest aggiunti per merge immutabile, quantità fuori limite e pilota assente. Test del nuovo store/UI, Vitest, lint, type-check e build non eseguiti dall'assistente. Il problema di formattazione precedente è stato dichiarato risolto dall'autore il 2026-10-19; non equivale a una verifica di queste nuove modifiche. Formattazione preparata manualmente: richiede verifica CI.

Nessuna migrazione aggiunta o applicata. Il vecchio store e le vecchie rotte restano per compatibilità. Restano da verificare in integrazione permessi, scadenza, recupero tra schede, navigazione mobile, popup e transizioni di stato. La fase non è dichiarata validata end-to-end.
