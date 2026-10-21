# Collaudo browser fase 15 SSE - esiti dichiarati

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione.
Codice di riferimento checklist iniziale: 8018d18, CI 39658083388 verde.
Fix iscrizioni successivo: 1226172, CI 39674942800 verde. Procedure estese originali
nella versione b1035c2 di questo file e nella storia Git. Nessun merge autorizzato.

## Riscontro registrato

Dichiarazione autore delle 22:39 CEST, non esecuzione manuale dell'assistente.
Commit locale, browser/versione e dispositivo non comunicati. Le righe non
verificate non sono PASS e non vengono coperte automaticamente dalla CI.

| Caso | Ambito | Esito autore |
|---|---|---|
| 1 | Ripresa e aggiornamento live | PASS |
| 2 | Conteggi locali e spunte con aggiornamento remoto | Non verificabile |
| 3 | Incompatibilita' e recupero confermato | Non verificabile |
| 4 | Cambio fase e sola lettura | PASS |
| 5 | Nuova revisione e autenticazione | PASS |
| 6 | Risultati gara e uscita | PASS |
| 7 | Canvas e interazioni | PASS |
| 8 | Connessione/fallback/resync | Non eseguito |
| 9 | Notifiche private e conferma selettiva | PASS |
| 10 | Errori e richieste lente | Non eseguito |

Sei PASS, due casi non verificabili e due non eseguiti. Il riscontro non dettaglia
se siano state provate tutte le varianti interne di ogni caso, ad esempio tutti
i dispositivi del caso 7. Nessun risultato aggiuntivo inventato.

Iscrizioni: segnalazione fuori dalla checklist iniziale alle 22:39 e precisazione
alle 22:41 per membri e osservatori autenticati non iscritti. Fix 1226172, quindi
richiesta di riprova di una nuova iscrizione con entrambe le sessioni aperte.
Alle 23:24 autore: "funziona". Conferma complessiva sul fix, non due log indipendenti.
Non si richiede di ripetere tutti i casi PASS per questo aggiornamento solo .md.

## Verifiche residue, se riprese

2. In due sessioni di prova, modificare una quantita' locale senza Prossimo e un
metadato compatibile remoto. Atteso: valore locale conservato, metadati aggiornati,
spunte interessate revocate; nessun salvataggio REST automatico.

3. Se la fixture e le azioni UI consentite lo permettono, ridurre totale o rimuovere
carta/pilota con modifica locale. Atteso: nessun clamp, copia conservata e conferma
bloccata. Rileggi inventario richiede dialogo: Annulla conserva, confermare crea
backup e azzera spunte senza confermare conteggi. Se non riproducibile resta non
verificabile, non PASS. Non forzare il database.

8. Con strumenti di rete nel solo client di prova, bloccare /api/events/stream
mantenendo REST disponibili. Attendere piu' intervalli effettivamente configurati;
atteso fallback, poi resync e arresto del polling quando torna open. Una sola
connessione attiva per scheda; connessioni terminate nei reconnect non sono duplicati.
Nessun retry di scritture. Senza strumenti adeguati lasciare non eseguito.

10. Nel solo ambiente isolato simulare errore/ritardo REST. Atteso: dati conservati,
errore visibile, nessuna bozza vuota fittizia. Cambiare contesto prima della risposta:
niente applicazione tardiva. Con fixture storage non scrivibile, recupero/apertura
sostitutiva deve interrompersi senza perdita della copia. Non cancellare backup.

## Vincoli e resoconto

Usare soltanto database e utenti di prova isolati. Questa checklist non autorizza
setup, heat.py start, migrazioni, reset o ripristini sull'originale; possono migrare.
Prima di uso reale servono arresto, backup verificato, prova su copia e permesso.
Nessun backup originale eseguito dall'assistente. Nessun npm audit fix/force,
aggiornamento dipendenze o svuotamento sessionStorage per simulare errori.

Per nuovi riscontri indicare caso, PASS/FAIL/NON ESEGUITO o non verificabile, ruolo,
commit locale, browser/dispositivo, passi e risultato. Screenshot o Console/Network
solo senza password, cookie, token o .env. Fermarsi su perdite di dati/scritture
inattese senza ripetere conferme alla cieca. La copia locale readonly non equivale
al risultato ufficiale e uscire non annulla HTTP gia' inviate.

Questo registro non certifica accessibilita', produzione o collaudo SSE completo
e non autorizza merge, migrazioni reali, risoluzione vulnerabilita' o fase 15b.
