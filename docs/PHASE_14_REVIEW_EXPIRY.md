# Fase 14j - Scadenza selettiva

Data: 2026-10-19. Ramo phase-14. Integra e aggiorna le note precedenti sulla scadenza, che non è più soltanto pianificata.

settle_expired_reviews richiama review_expiry.apply_expired_draft quando trova una bozza. Il piano considera tutte le carte; quelle coerenti vengono applicate insieme. Per una carta incongruente non cambia nessun inventario, quantità della pool o giocata di alcun pilota. La gara viene chiusa e la bozza mantenuta per consentire una successiva verifica amministrativa. Le carte escluse vengono annotate nel log.

Se tutte le carte sono coerenti, la bozza viene eliminata dopo l'applicazione. Se il JSON è corrotto, non si applica alcun cambiamento e la gara resta aperta. Senza bozza rimane il comportamento legacy. Non è introdotto un processo pianificato: come prima, la scadenza viene elaborata alla successiva chiamata del servizio, anche attraverso gli endpoint che già lo usano.

La bozza conservata dopo una chiusura parziale non è ancora accompagnata da una schermata di audit. Le giocate delle carte saltate restano inalterate; non si consumano successivamente in automatico sulla gara chiusa. Questo è un limite da gestire nell'interfaccia amministrativa.

Tre test di integrazione predisposti: applicazione parziale, bozza interamente valida e JSON corrotto. Non eseguiti dall'assistente; nessun successo CI dichiarato. La modifica non applica migrazioni e non tocca il database reale durante il commit.

Restano frontend, spunte e integrazione del popup. La conferma legacy resta disponibile per compatibilità e non applica la bozza: il frontend nuovo dovrà usare /review/counts/confirm. Queste note distinguono implementazione presente e verifiche ancora mancanti.
