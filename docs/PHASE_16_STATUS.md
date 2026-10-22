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

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.
