# Fase 15a-4a - Correzione della formattazione frontend

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14.
Integrazione di PHASE_15.md e PHASE_15_FRONTEND_CLIENT.md.

## Errore verificato

Commit cb5d649d72fe8b2a4765d43fc06e7b06d12411d8, run 39424794586:
backend pytest e migrazioni success, frontend failure.
Il log fornito dall'autore mostra npm run lint interrotto da prettier --check
su cinque file src/lib/events e src/routes/+layout.svelte. In quel tentativo
ESLint non viene eseguito dopo il fallimento del primo comando della catena;
non si dichiarano superati test e build di quel run fallito.

## Procedura pubblicata

Workflow .github/workflows/format-sse-client.yml introdotto in bf1ab11,
attivato solo da push che modificano il workflow stesso sul ramo fase 15.
Workflow storici diretti a main e phase-14 lasciati intatti.
Nessun pull_request_target o token nuovo.

Il job usa Node 22 come la CI, npm ci e il Prettier installato dal lockfile,
con prettier.config.js e plugin del repository invariati. Elenco esclusivo:

- frontend/src/lib/events/event-client.spec.ts
- frontend/src/lib/events/event-client.ts
- frontend/src/lib/events/event-types.ts
- frontend/src/lib/events/event-validation.spec.ts
- frontend/src/lib/events/event-validation.ts
- frontend/src/routes/+layout.svelte

Dopo prettier --write e --check il job esegue npm run lint, npm run check,
npm test e npm run build. Pubblica solo dopo la riuscita di tutti i comandi.
Lockfile, package.json e configurazione Prettier devono essere invariati.
Il push non usa force e viene rifiutato se la testa del ramo e' cambiata.
Il permesso contents: write e' limitato al job che pubblica la formattazione.

## Esito verificato

Commit bot pubblicato il 2026-10-20 alle 14:52:10 CEST:
33f01f0447706cbfe78a7468b4e0c7cb13696deb.
Messaggio: style: formatta client SSE con Prettier del lockfile.
Dettagli del commit verificati: esattamente i sei file sopra elencati.

Verificata anche la CI ordinaria sulla nuova testa, senza presumere che il
push bot bastasse ad avviarla: run 39425660561, tutti i job success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39425660561

- Frontend check/lint/test/build: concluso alle 15:03:35 CEST.
- Backend pytest: concluso alle 15:04:41 CEST.
- Migrazioni su database di test: concluso alle 15:03:02 CEST.

L'errore di formattazione e' risolto sulla testa 33f01f0. Non sono stati letti
i log completi del job format ne' i conteggi test: la verifica si basa sul
commit bot effettivamente presente e sui tre esiti della CI ordinaria.
Nessun npm, formatter, lint, check, test o build eseguito localmente dall'assistente.
Un nuovo commit documentale richiede una verifica CI separata.

## Riscontro dell'autore e perimetro residuo

Alle 15:23 CEST del 2026-10-20 l'autore ha riferito "ok per ora va tutto".
Riscontro positivo non dettagliato; non viene equiparato a tutti i casi della
checklist manuale o a una validazione end-to-end della sincronizzazione SSE.

Nessuna modifica alle regole SSE, al polling, alle dipendenze o al database
in questa correzione. Le schermate restano da collegare nella 15a-4b, previa
analisi e approvazione separata. Nessun merge autorizzato.
