# Fase 16 - Formattazione UI e navigazione gia' risolta

Aggiornamento: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory. Nessun merge.

## Formattazione pubblicata

Il primo log dell'autore mostrava prettier --check fermato sui quattro componenti
admin. 2cf25fd ha separato la pubblicazione dello stile dai controlli applicativi
successivi. Il bot ceb12b1 ha effettivamente pubblicato la formattazione dei soli
admin-card-container, admin-championship-pilots, admin-pilot-cards-panel e
championship-settings. Il nuovo log fornito dall'autore riporta All matched files
use Prettier code style: quel controllo e' passato, non l'intera suite frontend.

## Blocco ESLint distinto

Dopo Prettier il log riporta un errore svelte/no-navigation-without-resolve sulla
chiamata goto(target.url) in admin-pilot-cards-panel.svelte, linea 82 nella versione
formattata letta. target.url viene memorizzata da navigation.to.url.href dentro
beforeNavigate: e' la destinazione completa ricevuta da SvelteKit, non una nuova
rotta costruita dalla UI. Il ramo unload usa gia' location.assign separatamente.

La modifica aggiunge un commento sulla provenienza della URL e una sola direttiva
eslint-disable-next-line svelte/no-navigation-without-resolve immediatamente prima
di goto. L'eccezione e' limitata a questa ripresa di navigazione gia' risolta; non
disabilita la regola per il file o nel progetto e non introduce cast, nuove
dipendenze, concatenazioni di base o trasformazioni della destinazione.
Il codice eseguibile, la conservazione della bozza su errore e le conferme
restano invariati. Questa eccezione non va estesa alle nuove rotte dell'app.

## Verifiche e limiti

Nessuna nuova esecuzione locale di npm, lint, Vitest o browser in questo intervento.
Il passaggio di lint del log e' fallito su ESLint; non dichiarare test e build
riusciti. La correzione deve ancora essere verificata con la toolchain del progetto.
Il workflow conserva Prettier dal lockfile, check, lint, test e build e stampa
la SHA del codice controllato. Un commit del formatter non prova il verde globale
e non garantisce una nuova CI ordinaria: verificare le SHA e i job effettivi.
Nessuna modifica al workflow in questo intervento, al database o alle dipendenze.
Restano esclusi PUT dalla UI, autosalvataggio e live. Dopo i controlli riusciti
riallineare il documento sorgente della fase, quello della UI e i documenti generali;
nessuna attesa di test applicativi per i soli commit documentali.
