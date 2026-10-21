# Lifecycle revisione e controllo canvas

Stato: patch preparata, applicazione e controlli ancora da verificare.
Base frontend invariata dopo cc8ba7a/1145a9a; solo phase-15-sse-sistemazione.
Nessun merge o intervento sui dati reali autorizzato.

## Tentativi e correzioni

9a0ef20, verify 39654061238: arresto iniziale. La vecchia ancora !this.disposed &&
ha due occorrenze; 5908cc6 limita la sostituzione alla firma e prime righe del
getter active, lasciando refreshStatus invariato. Analisi ricavata dal codice letto.

5908cc6, verify 39655437138: log autore delle 20:56 CEST del 2026-10-21.
npm ci, formatter e lint riusciti. svelte-check riporta 0 errori e 1 warning:
canvas non puo' avere role img, a11y_no_interactive_element_to_noninteractive_role.
La guardia diagnostica interrompe correttamente il job: test/build non eseguiti,
nessun commit bot. La CI ordinaria verde continua a riferirsi al codice gia' pubblicato.

Correzione ulteriore: rimuovere soltanto role img, mantenendo aria-label, controllo
button nativo, focus e comandi. Nessuna soppressione o rimozione della guardia.
Il workflow breve esegue il solo blocco Python approvato dal commit immutabile
5908cc656324dc34e7de03513059ca7087a19fa1; checkout include il genitore per leggerlo.
Quel blocco verifica tutti e cinque i blob frontend. Dopo l'applicazione si rimuove
una sola occorrenza del ruolo canvas; basi diverse interrompono la pubblicazione.
Non esegue ricorsivamente il nuovo workflow e non scarica script esterni.

## Modifica funzionale conservata

Pannello gia' mostrato conservato nello stesso contesto gara/utente, senza stato
nella key; flag azzerato al cambio contesto. Resta nascosto senza ruolo di gestione
gare. enabled=canReview limita editing e canOpen; effetto con untrack inoltra il
limite allo store. False revoca spunte e congela scritture senza sostituire copie;
true richiede nuova lettura. Verifica preinvio, apertura e recupero rispettano il
limite. Backend autorevole, nessuna cancellazione di HTTP gia' partite.

Canvas senza ruolo esplicito non consentito; gestori sul button nativo con nome
accessibile. Trascinamento tramite panView e larghezza canvas, frecce per spostare,
Maiusc per passo fine, Invio/Spazio per esportare. Zoom, dimensioni e WebP invariati.
Nessuna dichiarazione di accessibilita' completa prima del collaudo browser.

## Controlli e seguito

Tre test store con API simulate: sola lettura preserva copia e blocca scritture,
limite cambiato durante verifica impedisce PUT, riabilitazione rilegge e revoca
spunte. Suite precedenti conservate; nessun nuovo test DOM o dipendenza.
Formatter, lint, check con guardia canvas, test e build precedono il commit dei
cinque file frontend e nota. Testa ramo verificata prima del push, nessun force.
Questo commit prepara soltanto workflow e nota; verificare job, bot e CI della
nuova testa prima di dichiarare applicazione riuscita. Nessun npm locale eseguito.

Restano verifica browser di cambio fase, permessi, dialoghi, focus, tastiera,
mouse/touch e uscita durante HTTP. Dopo verde riallineare le note interessate e
preparare avviso/checklist finale se non emergono altri blocchi. SSE non certificato
dalla sola CI. Backend, API, SQLite, lockfile e documenti protetti intatti.
Vulnerabilita' npm gia' segnalate non risolte; nessun audit fix/force.
