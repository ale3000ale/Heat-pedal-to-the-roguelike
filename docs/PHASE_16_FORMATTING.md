# Fase 16 - Correzione del flusso di formattazione UI

Data: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory. Nessun merge.

## Errore osservato

Il log fornito dall'autore mostra npm run lint fermato da prettier --check
sui quattro componenti admin-card-container, admin-championship-pilots,
admin-pilot-cards-panel e championship-settings. ESLint non viene eseguito
in quel comando perche' segue Prettier con &&. Il job format risultava
fallito nella lettura precedente; questo riepilogo non identifica quale
suo passaggio sia fallito e non inventa un errore TypeScript o ESLint.

## Modifica circoscritta

format-review-ui.yml usa ancora npm ci e il Prettier del lockfile. Dopo write
e check dei soli quattro componenti puo' pubblicare solo quei file, conservando
il controllo del ramo remoto e la protezione dei percorsi estranei. La pubblicazione
della correzione di stile precede ora check, lint, test e build; tutti restano
presenti, senza continue-on-error, esclusioni o modifiche alla CI ordinaria.
Il workflow stampa la SHA locale effettivamente sottoposta ai controlli.
Un eventuale commit del bot dimostra solo la pubblicazione dello stile dopo
Prettier, non il successo dei controlli applicativi successivi o del browser.

## Verifica ancora necessaria

Nessuna esecuzione locale del workflow o di npm in questo intervento.
Controllare l'esecuzione del formatter, l'eventuale commit con soli quattro file
e i controlli sul codice formattato. Non assumere che il commit del bot attivi
automaticamente una nuova CI ordinaria: verificare la SHA di ogni riscontro.
La modifica rende indipendente la pubblicazione dello stile ma non dimostra
che il blocco segnalato sia gia' risolto. Nessun accesso al database, cambiamento
di dipendenze, PUT, autosalvataggio o integrazione live.
Dopo i controlli riusciti riallineare il documento sorgente della fase, il documento
della UI e i documenti generali, senza attendere test per i soli commit docs.
