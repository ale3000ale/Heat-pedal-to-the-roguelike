# Fase 16 - Riallineamento e lettura tecnica iniziale

Data: 2026-10-22. Solo phase-16-admin-pilot-inventory.
Stato: riallineamento preparato, pubblicazione automatica ancora da verificare.
Specifica approvata f87a759; base main 6dcdc836dba33a506bd954cd27eda3d212ba84ad,
merge PR 14. Questo blocco non implementa la funzionalita'.

## Documenti

Workflow vincola le versioni lette di PROJECT_SPEC.md, PROJECT_STATUS.md,
PROJECT_NOTES.md, PHASE_16_SPEC.md e PHASE_16_STATUS.md. Conserva tutto il resto dei
documenti generali lunghi e copia le sezioni operative della specifica gia' approvata
in una nuova appendice del master. Non ricostruisce il testo da risposte troncate.
Registra il merge reale della fase 15, avvio documentale della 16 e approvazione
senza dichiarare backend/frontend completati. Corregge solo l'intestazione/formula
di approvazione dei documenti 16, senza cambiare regole gia' concordate.

Git diff --check, titoli e perimetro prima del commit dei sei .md. Arresto su basi
o testa cambiate, niente force push. Il primo commit prepara workflow e nota;
leggere esito e bot per confermare il riallineamento. Nessun npm/pytest eseguito
in questo blocco solo documentale, nessun esito applicativo attribuito alla sua CI.

## Evidenze tecniche

Modello Pilot letto: tre Deck distinti. Modello Deck letto: cards persistito come
stringa e version con version_id_col di SQLAlchemy. Nessuna modifica a colonna,
formato JSON, schema o immagini proposta da questo riallineamento. Non e' un'analisi
del file SQLite originale: nessun DB originale aperto o modificato.

shop_purchase._lock_database letto: su SQLite prende BEGIN IMMEDIATE prima delle
letture quando non c'e' gia' una transazione nativa aperta; altrimenti non aggiunge
un nuovo blocco. create_race lo usa gia' ma non verifica la dimensione dei mazzi.
move_card legge stato e mazzi e usa versioni/retry, ma non prende quel blocco prima
delle letture. Per la nuova regola da 15 copie non basta aggiungere un controllo
frontend o un confronto versioni ai soli salvataggi admin: il blocco backend dovra'
coordinare avvio e modifica mazzo del giocatore per evitare decisioni su letture vecchie.
Questa esigenza e' analizzata, non gia' implementata o verificata in concorrenza.

## Blocco applicativo successivo

Definire e mostrare file, API/DTO e test prima della pubblicazione: elenco piloti
admin con username, snapshot dei cinque contenitori, salvataggio unico e validato,
lettura/aggiornamento con versioni e controllo di ruolo/iscrizione/gara/revisione.
Mantenere le cinque direzioni concordate e le copie fisicamente separate; nessuna
aggiunta diretta dalla pool al mazzo e nessuna doppia sottrazione. Salva confermato
con riepilogo testuale, immagini nelle altre sezioni. Backend primo, poi frontend.

Controllo esatto di 15 copie all'avvio per tutti gli iscritti, senza cambiare
l'inventario iniziale o rendere obbligatori 15 durante la preparazione. Aggiornare
fixture di prova, non dati di produzione. Live tramite client condiviso e REST
autorizzate, senza nuova esposizione di carte private o notifiche regalo inventate.
Non estendere altri CRUD o diritti del giudice. Nessun endpoint/evento nuovo gia'
introdotto da questi documenti e nessuna nuova dipendenza/migrazione dichiarata.

Nessuna modifica a main, applicazione, dati, immagini, dipendenze o lockfile.
Nessun setup, avvio, reset, backup o migrazione sul DB reale autorizzato. Tutti i
nuovi test, controlli automatici e prove browser della fase 16 restano da eseguire.
