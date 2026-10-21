# Fase 15a-4b - Riconciliazione conservativa degli inventari di revisione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Modulo e test verificati su 6aa7fe6 in CI 39599465230. Store e pannello non lo
usano ancora: primo sottoinsieme, non nuova sincronizzazione interna completata.

## Politica approvata e modulo

Proposta seguita alle 14:15: conservare conteggi locali incompatibili, bloccare
conferma senza clamp, revocare spunte interessate, non trasferire bozze a un altro
revisore/inizio e richiedere conferma per riletture che abbandonano modifiche.
Modulo calcola il risultato; blocchi UI, spunte, dialogo e lifecycle ancora da collegare.

review-inventory-reconcile.ts usa base server, copia locale e nuovo remoto con
bozza server gia' applicata, nella stessa revisione propria. ownReviewKey distingue
gara/revisore/inizio solo per il proprio stato attivo. Non autorizza HTTP e non
sostituisce il controllo server della scadenza; il chiamante confronta le chiavi
prima del merge e impedisce bozze trasferite a un altro contesto.

Remaining locali modificati preservati con nuovi metadati/carte remoti.
changedPilotIds rileva dati carte rispetto alla base, non riordini o solo nome
pilota. conflictingPilotIds segnala conteggi concorrenti validi da ricontrollare.
Carte/piloti rimossi con modifiche o conteggi oltre il nuovo totale producono
issues/blocked e l'intera copia locale resta intatta. Nessuna riduzione o scarto
silenzioso. Duplicati normalizzati e fonti server non valide generano RangeError,
mai fallback a []. Risultati restituiti come copie indipendenti; nessuna REST di scrittura.

## Fonti e verifiche effettive

Rilette API review_counts.py e race_review.py: inventario giudice/admin leggibile
senza titolarita', bozza solo titolare attivo. GET stato puo' gia' elaborare
scadenze sul server; il nuovo client non deve introdurre conferme/salvataggi agli
eventi. 403/409 per cambio proprietario durante letture: rileggere lo stato,
non interpretare bozza non leggibile come bozza vuota o permesso di scrittura.

Implementazione 05b282984b492fdf3a666c2383d40b938e7e6c19. Bot
6aa7fe6c4b2307550aa3f229b0a3f99810d1a67a alle 14:25:19 CEST del 2026-10-21.
Letto il diff: sola formattazione di modulo e .spec.ts, nessun cambio logico.
Il workflow aveva i soli due nuovi TypeScript e verifiche complete dal lockfile;
si ferma se il ramo cambia senza force push. Nessuna dipendenza/versione nuova.

CI ordinaria sulla testa formattata: 39599465230, tutti i job success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39599465230

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Migrazioni (database di test) | success | 14:26:26 |
| Frontend (check, lint, test, build) | success | 14:26:47 |
| Backend (pytest) | success | 14:28:04 |

Suite passata: chiave propria/nuovo inizio, fonti pulite, conteggi locali, nuove
carte, immutabilita', totale ridotto, carta/pilota rimosso, conflitto valido,
snapshot vuoto riuscito e input invalidi. Test puri, non store o DOM. Verificati
esiti, commit e diff, non log completi formatter o conteggi numerici. Nessun comando
npm, formatter, lint, check, test o build locale eseguito dall'assistente.

## Seguito

Riallineamento di questa nota, PHASE_15.md, nota gara e nota risultati: soli .md,
non blocca il seguito in attesa CI e non attribuisce esiti presunti a quel commit.
Nessuna modifica a codice, workflow, dipendenze, API, schema, immagini o dati qui.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Collegare ora realmente store e
pannello: stato/proprietario, sottoscrizioni/fallback, merge nella stessa chiave,
revoca spunte, blocchi conferma e recupero esplicito confermato con test lifecycle,
permessi, errori, 401 e risposte tardive. Non introdurre altri prerequisiti backend.
Warning canvas e prove browser separati e pendenti. Nessun test manuale finale
richiesto ora: avviso dopo collegamenti restanti e relativi controlli verdi.
Nessun merge o intervento sui dati reali autorizzato. Il merge frontend non crea
concorrenza protetta lato server.
