# Fase 16 - Collegamento del salvataggio alla UI admin

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, migrazione, dipendenza nuova o accesso diretto al database reale.

## Baseline osservata

Client PUT introdotto in 549e83e e formattato in f95c915. Piano puro introdotto
in 024d47a e formattato dal bot ad377d4. Nella lettura della CI 40009944027 su
ad377d4, frontend (check, lint, test, build), job 120611039888, e migrazioni
risultano riusciti; backend ancora in corso in quella lettura. Questi stati non
sono prove browser o una nuova esecuzione locale.

Il contratto backend resta versions per tutti i contenitori e transfers source/path.
Solo le due pool possono essere null. Il piano copia le versioni dalla baseline,
ricalcola senza fidarsi dell'anteprima memorizzata e produce una riga per clic in
ordine, non un riepilogo delle differenze nette. Client e piano non ritentano.

## Nuovo incremento UI

admin-pilot-cards-save-controls.svelte separa riepilogo, conferma unica e rete
dal rendering delle carte. Riepilogo e salva prepara una proposta; Annulla, X,
Escape o sfondo la cancellano senza PUT. Conferma e salva consuma la proposta
e imposta il blocco prima del primo await. Una seconda invocazione non invia
un'altra richiesta. Se la sessione non e' piu' quella proposta, richiede un nuovo
riepilogo. Il salvataggio usa esattamente la richiesta preparata per la conferma.

Durante conferme, PUT e rilettura lo stato occupato risale a elenco piloti e
impostazioni: clic carte, ripristino, ritorno e chiusura ordinaria vengono bloccati.
La navigazione normale viene annullata. Il browser puo' comunque consentire una
chiusura forzata: questo non annulla una scrittura gia' inviata. Le risposte di
un componente dismesso o di una sessione sostituita vengono ignorate.

Su successo viene creata una nuova sessione dallo snapshot PUT, con registro
vuoto e versioni server, senza GET automatica. Gli errori conservano la bozza.
Un 422 lascia possibile una nuova azione manuale, non un retry automatico.
Altri errori bloccano altri invii: 401/403/404/409 come rifiuto/conflitto, gli
altri come esito non verificato che potrebbe essere gia' stato applicato.
La risposta viene controllata dal client per contesto e dalla creazione della
sessione per le carte; non e' una nuova validazione runtime completa del DTO.

Rileggi dal server e' un'azione esplicita. Con operazioni pendenti richiede
conferma; lo scarto avviene soltanto dopo una risposta utilizzabile. Su errore
restano baseline, anteprima e registro precedenti. Ripristina bozza resta locale
e conserva l'eventuale blocco: non sostituisce la rilettura dopo un conflitto.

## Verifiche e limiti

Questo incremento modifica quattro componenti, formatter circoscritto e questo
documento. Nessuna nuova esecuzione locale di npm, lint, Vitest, build o browser.
I test del client, del piano e della sessione non provano queste nuove interazioni
Svelte; non sono aggiunti test DOM in questo passaggio e non si dichiara PASS.
Il formatter conserva lockfile, Prettier e controlli completi dopo il commit dello
stile. La CI ordinaria non cambia. Verificare le SHA dei controlli effettivi.

Prima di dichiarare il flusso collaudato verificare: annullamento senza PUT,
conferma singola e doppi clic, successo con versioni nuove, 409 e rete incerta,
422, rilettura fallita senza perdita della bozza, annullamento con Escape,
chiusura/ritorno durante rete e risposte tardive. Dopo CI riuscita riallineare
il documento sorgente, quello della UI e i documenti generali senza attendere
nuovi test per i soli commit docs. Nessun polling, autosalvataggio o nuovo stream
SSE. Il live resta successivo e la fase 16 non e' completa.
