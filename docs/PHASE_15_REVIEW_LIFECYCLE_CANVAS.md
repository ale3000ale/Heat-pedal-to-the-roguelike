# Lifecycle revisione e controllo canvas

Stato: patch preparata, applicazione e controlli ancora da verificare.
Base cc8ba7a, dopo collegamento 1145a9a e CI 39650297363 verde. Solo ramo
phase-15-sse-sistemazione. Nessun merge o intervento sui dati reali autorizzato.

## Valutazione e modifica prevista

Pagina gara letta: canReview puo' diventare false e la key include race.status.
Questo smonta il pannello al cambio fase, perdendo la copia visibile in memoria.
La patch conserva il pannello gia' mostrato nel medesimo contesto gara/utente,
toglie lo stato dalla key e azzera il flag al cambio contesto. Lo nasconde ancora
quando manca il ruolo di gestione gare, senza esporre copie a un altro utente.

Il genitore passa enabled=canReview e limita canOpen. Il pannello inoltra il limite
allo store tramite effetto con untrack, senza dipendenze reattive involontarie.
False disabilita editing e scritture, revoca spunte ma non sostituisce conteggi;
true richiede nuova lettura. Verifica preinvio ricontrolla anche questo limite.
Apertura e recupero confermati non aggirano il limite. SSE rimane una lettura e
non concede permessi; backend ancora autorevole, HTTP gia' partite non annullate.

Canvas letto: role img con gestori pointer. La patch mantiene il canvas come
immagine senza gestori e sposta interazione su un button nativo con nome accessibile.
Trascinamento usa la stessa panView e la larghezza del canvas; frecce spostano,
Maiusc usa passo fine, Invio/Spazio esportano. Zoom e dimensioni/WebP invariati.
Focus visibile, istruzioni aggiornate, nessuna soppressione a11y o finto ruolo.

## Verifiche e confini

Workflow vincola i cinque blob frontend, applica sostituzioni univoche e aggiunge
tre test reali dello store con API simulate: sola lettura preserva copia e blocca
scritture, limite cambiato durante verifica impedisce PUT, riabilitazione rilegge
e revoca spunte. Nessun nuovo test DOM o dipendenza. Suite precedenti conservate.
Formatter, lint, check, test e build prima del commit sui cinque frontend e nota;
se check riporta diagnostica di card-crop-editor.svelte il workflow si ferma.
Guardia testa ramo e niente force push. Questo commit prepara solo workflow/nota.

Nessun npm locale eseguito dall'assistente. Non dichiarare riuscita prima di job,
bot, diff e CI ordinaria. Compilazione e test dello store non provano DOM: restano
verifica browser di cambio fase, nuove autorizzazioni, dialoghi, focus, tastiera,
mouse/touch e uscita durante HTTP. Non dichiarare accessibilita' o SSE complessivi
certificati dalla sola CI. Dopo verde riallineare le note interessate e preparare
l'avviso/checklist manuale finale se non emergono altri blocchi.

Backend, API, SQLite, dipendenze, lockfile e documenti protetti intatti. Nessuna
migrazione, reset o modifica ai dati reali. Vulnerabilita' npm segnalate dal blocco
precedente non risolte qui; nessun audit fix/force.
