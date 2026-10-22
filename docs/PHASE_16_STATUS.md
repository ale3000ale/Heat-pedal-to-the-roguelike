# Stato fase 16

Data: 2026-10-22. Ramo phase-16-admin-pilot-inventory, creato da main 6dcdc83.

## Raccolta requisiti

17:42: sezione admin Piloti nelle opzioni campionato, proprietario e icona carte,
inventari/pool del campionato apribili, trasferimenti e salvataggio live fuori gara.
17:49: blocco anche in revisione, rimozione possibile delle carte nel mazzo,
nuova regola di avvio con tutti i mazzi da 15 copie.
17:57: tre contenitori distinti per il pilota: mazzo, inventario Modifiche e Sponsor.
18:00: mazzo cliccabile verso pool; pool verso soli inventari, mai mazzo; modal di
conferma Salva con elenco testuale, immagini nelle sezioni delle carte.

Specifica consolidata in PHASE_16_SPEC.md, sottoposta all'approvazione con questo
push. Lettura iniziale di impostazioni campionato, servizi gare/mazzo e modello
Pilot effettuata. Nessuna implementazione, API nuova o migrazione gia' completata.
Nessun npm/pytest, test locale o browser della nuova funzionalita' eseguito.

Prossimo passo dopo approvazione: riallineamento della specifica/stato generale,
analisi tecnica delle operazioni atomiche e della concorrenza, poi backend e
frontend in blocchi approvati e verificati. Non modificare main o database reale;
nessuna PR unita e nessun nuovo requisito di gioco aggiunto fuori dalla specifica.
