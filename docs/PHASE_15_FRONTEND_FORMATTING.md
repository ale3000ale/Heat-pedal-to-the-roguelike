# Fase 15a-4a - Correzione della formattazione frontend

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14.
Integrazione di PHASE_15.md e PHASE_15_FRONTEND_CLIENT.md.

## Errore verificato

Commit cb5d649d72fe8b2a4765d43fc06e7b06d12411d8, run 39424794586:
backend pytest e migrazioni success, frontend failure.
Il log fornito dall'autore mostra npm run lint interrotto da prettier --check
su cinque file src/lib/events e src/routes/+layout.svelte. ESLint non viene
eseguito quando il primo comando della catena fallisce; test e build sono
passaggi successivi del workflow CI e non vengono dichiarati superati.

## File e procedura proposta

Nuovo .github/workflows/format-sse-client.yml, attivato solo da un push che
modifica il workflow stesso sul ramo fase 15. I workflow storici diretti a
main e phase-14 sono lasciati intatti. Nessun pull_request_target o token nuovo.

Il job usa Node 22 come la CI esistente, npm ci e il Prettier installato dal
package-lock.json, con prettier.config.js e plugin del repository invariati.
La scrittura riguarda esclusivamente:

- frontend/src/lib/events/event-client.spec.ts
- frontend/src/lib/events/event-client.ts
- frontend/src/lib/events/event-types.ts
- frontend/src/lib/events/event-validation.spec.ts
- frontend/src/lib/events/event-validation.ts
- frontend/src/routes/+layout.svelte

Dopo prettier --write e --check esegue npm run lint, npm run check, npm test
e npm run build. Solo se tutti riescono pubblica i sei file formattati con un
commit bot sullo stesso ramo. Lockfile, package.json e configurazione Prettier
devono essere invariati. Il push non usa force e viene rifiutato se la testa
del ramo e' cambiata rispetto al checkout verificato.
Il job dispone di contents: write per il solo commit di formattazione.

## Stato reale delle verifiche

Workflow e configurazione del formatter riletti. Nessun npm, Prettier, lint,
check, test o build eseguito localmente. Il job qui descritto non e' ancora
stato eseguito: occorrono approvazione, push e lettura del suo esito.
Se uno dei controlli fallisce non pubblica il commit di formattazione;
va letto l'errore prima di preparare una correzione separata.

La CI ordinaria puo' fallire ancora sul commit che introduce il job, perche'
quel commit non contiene ancora i file formattati. Non confondere questo
run con il risultato del job Formatta client SSE sulla copia formattata.
Un commit bot tramite GITHUB_TOKEN potrebbe non avviare la CI ordinaria:
verificare esplicitamente la nuova testa, senza presumere nuovi check verdi.
Dopo la riuscita, riallineare PHASE_15.md e PHASE_15_FRONTEND_CLIENT.md con
commit e risultati reali. Nessuna riuscita preventiva dichiarata.

Nessuna modifica alle regole SSE, al polling, alle dipendenze o al database.
Le schermate restano da collegare nel blocco 15a-4b; nessun merge autorizzato.
