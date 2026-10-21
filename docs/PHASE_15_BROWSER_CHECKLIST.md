# Collaudo browser fase 15 SSE

Data: 2026-10-21. Stato: DA ESEGUIRE, nessun caso marcato riuscito dall'assistente.
Codice di riferimento: 8018d189dcef770a76093c59489566cdeccd4dc6 sul ramo
phase-15-sse-sistemazione, CI 39658083388 verde. Commit successivi solo documentali
non richiedono di rieseguire vecchi workflow di applicazione. Nessun merge autorizzato.

## Avviso e sicurezza

Le correzioni automatiche previste sono pubblicate e verificate. Serve ora una
prova browser: CI e test simulati non sostituiscono le interazioni reali.
Usare esclusivamente un ambiente isolato con database e utenti di prova, non il DB
originale. Se l'ambiente non e' gia' predisposto e verificato, fermarsi: questa
checklist non autorizza setup, heat.py start, migrazioni, reset o ripristini sul DB
reale. Questi comandi possono migrare. Nessun backup originale e' stato eseguito
dall'assistente. Preparazione sicura della copia e relativi permessi sono separati.

Non usare npm audit fix/force e non aggiornare dipendenze per eseguire i casi.
Non svuotare sessionStorage o cancellare backup per simulare errori. Le azioni di
gioco sotto sono scritture intenzionali sui soli dati di prova.

## Preparazione

- Annotare commit locale, browser/versione e dispositivo. Deve essere incluso 8018d18.
- Predisporre un campionato aperto, una gara e inventari sponsor con quantita' note.
- Usare sessioni autenticate indipendenti: un gestore titolare della revisione e
  un secondo utente con i permessi necessari alle azioni di prova. Le notifiche
  private richiedono anche una sessione del giocatore destinatario.
- Annotare conteggi iniziali/bozza salvata. Non forzare proprietario, scadenza o stato
  modificando SQLite o chiamando API non previste dall'interfaccia.
- Per ogni caso registrare PASS, FAIL oppure NON ESEGUITO, con passi e risultato.

## Casi principali

### 1. Ripresa e aggiornamento live

Aprire la pagina di una revisione propria gia' attiva. Verificare recupero conteggi
e countdown senza acquisizione/apertura automatica al solo ingresso. Nell'altra
sessione effettuare una modifica inventario consentita. La prima deve aggiornarsi
senza ricaricare la pagina. Il solo evento non deve salvare o confermare conteggi.
Se i permessi impediscono l'azione di prova, annotarlo senza aggirare il backend.

### 2. Modifiche locali e spunte

Nella prima sessione cambiare una quantita' senza Prossimo. Dalla seconda cambiare
un dato compatibile dello stesso inventario. Verificare che il conteggio locale
modificato resti, i metadati si aggiornino e i piloti interessati perdano la spunta.
Prossimo salva solo su richiesta. Conferma deve richiedere tutti i piloti controllati.

### 3. Incompatibilita' e recupero

Se ottenibile con azioni UI consentite, rendere incompatibile una modifica locale
per rimozione carta/pilota o nuovo totale ridotto. La copia non deve essere ridotta
silenziosamente; editing/conferma devono bloccarsi. Rileggi inventario deve chiedere
conferma: Annulla conserva il lavoro, confermare azzera spunte e mostra la copia
precedente. Nessun conteggio deve risultare confermato dalla sola rilettura.
Se il caso non e' riproducibile con la fixture annotare NON ESEGUITO, non PASS.

### 4. Cambio fase e sola lettura

Con copia locale presente, effettuare una transizione consentita che renda quella
gara non piu' revisionabile, oppure attendere la scadenza effettiva sul server.
Non modificare il DB per anticiparla. A parita' di gara/utente e ruolo di gestione,
il pannello gia' mostrato deve restare, con copia locale non confermabile quando
lo stato non lo consente. La copia locale non e' il risultato ufficiale applicato
alla scadenza: confrontare separatamente l'ultima bozza salvata e i dati ufficiali.
Nuova gara, altro utente o perdita ruolo non devono esporre o trasferire quella copia.

### 5. Nuova revisione e autenticazione

Seguendo solo le operazioni consentite, rinunciare/cambiare titolare o aprire un
nuovo inizio revisione. La vecchia copia non deve passare automaticamente alla
nuova chiave; recupero sostitutivo con conferma. Provare logout e login diverso
con richieste in corso: niente dati del vecchio contesto o aggiornamenti tardivi
sulla nuova vista. Eventuali azioni gia' inviate non vengono annullate dal logout.
Verificare che pulsanti e blocchi rispettino ruolo/stato, senza aggirarli via API.

### 6. Risultati gara e uscita

Modificare ordine/assenti/sponsor e generare un aggiornamento remoto compatibile.
La bozza locale deve conservarsi; conflitti segnalati, permesso perso significa
sola lettura. Ogni iscritto va assegnato una volta. Uscita con modifiche o PUT in
corso deve richiedere conferma; Rimani conserva la pagina. Uscire non annulla una
PUT gia' inviata: verificarne separatamente l'esito ufficiale.

### 7. Canvas mouse, touch e tastiera

Caricare un'immagine di prova nell'editor, provare drag, zoom e ritaglio WebP.
Con tastiera raggiungere il controllo: focus visibile, frecce spostano, Maiusc
consente passo fine, Invio/Spazio applicano. Non deve inviare accidentalmente il
modulo di caricamento. Provare anche touch se disponibile; se non disponibile
registrare NON ESEGUITO. Nessuna certificazione di accessibilita' completa da questo caso.

## Casi aggiuntivi con strumenti di rete

### 8. Connessione, fallback e resync

Se possibile, osservare una sola connessione stream attiva per scheda autenticata;
righe concluse da riconnessioni non sono duplicati attivi. Bloccare solo
/api/events/stream nel client di prova mantenendo REST disponibili. Attendere piu'
intervalli configurati e verificare fallback. Sbloccare: ritorno allo stream,
rilettura/resync e fine polling periodico mentre open. Nessun retry di scritture.
Non interrompere il server/database reale; senza strumenti adeguati segnare NON ESEGUITO.

### 9. Notifiche private e conferma selettiva

Assegnare un regalo di prova al giocatore autenticato: popup solo al destinatario,
non agli altri utenti. Confermare solo regali effettivamente resi, evitando ack per
annulli o chiusure remote. Verificare annullamento da altra sessione e ritorno della
connessione senza popup ricreati dal replay. Annotare ID fittizi e conteggi prima/dopo.

### 10. Errori e richieste lente

Nel solo ambiente isolato simulare errore REST o ritardo senza cancellare dati.
Copia locale conservata, errore visibile, nessuna bozza vuota fittizia. Navigare
verso altro contesto prima della risposta: niente applicazione tardiva o duplicazioni.
Se disponibile una fixture con storage non scrivibile, recupero/apertura sostitutiva
deve fermarsi, non perdere la copia. Non cancellare backup per ottenere questo caso.

## Resoconto

Per ciascun caso inviare ID, PASS/FAIL/NON ESEGUITO, ruolo, browser/dispositivo,
passi, atteso e osservato; per errori aggiungere screenshot o righe Console/Network.
Non includere password, cookie, token o .env. Fermarsi su perdite di dati o scritture
inattese, senza ripetere conferme alla cieca. Non dichiarare riusciti casi saltati.
Il riscontro aggiornera' lo stato fase; non autorizza automaticamente merge,
migrazioni reali, produzione, risoluzione vulnerabilita' o apertura della fase 15b.
