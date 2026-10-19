# Fase 14j - Servizio transazionale

Data: 2026-10-19. Ramo phase-14. Integrazione alle note della fase 14.

review_commit.py collega il piano puro ai dati SQLAlchemy. Legge tutti gli iscritti e tutte le giocate attive/consumate della gara senza mascherare quantità negative. Include carte con disponibilità zero nei dati della pool. Il massimo segue ancora il prototipo della pool; se assente non si verifica il limite superiore.

save_review_counts conserva una richiesta validata come JSON in race.review_draft. commit_review_counts richiede giudice/admin titolare di una revisione attiva. Apre il blocco SQLite esistente prima delle letture, controlla tutte le carte e applica il saldo finale di inventari e pool insieme al registro delle giocate in un commit. Non richiama consume_plays, evitando doppi consumi. Una conferma ripetuta sulla gara già chiusa viene rifiutata dalle regole esistenti.

In caso di incongruenze salva soltanto la bozza e solleva ReviewPlanConflict con il piano; la gara rimane in revisione. Gli altri errori causano rollback. Gli inventari e la pool vengono nuovamente validati prima della scrittura JSON.

Quattro test di integrazione predisposti: consumi corretti, conflitto con sola bozza, bozza senza movimento e correzione dopo riapertura. Non eseguiti nell'ambiente dell'assistente; nessun esito CI dichiarato. Restano validi soltanto i 10 test del calcolo puro eseguiti nel passaggio precedente, non come prova di questo servizio.

Nessuna rotta o interfaccia è modificata da questo commit. La conferma esistente continua a usare il vecchio servizio finché non verrà collegato quello nuovo. Restano da implementare lettura della bozza, gestione delle spunte, scadenza selettiva, integrazione API, test ulteriori di permessi/concorrenza e frontend. Nessun backup creato e nessuna migrazione applicata al database reale.
