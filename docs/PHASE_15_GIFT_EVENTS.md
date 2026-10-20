# Fase 15a-3 - Eventi tasto S e annullamento assegnazione

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md e PHASE_15_CARD_PLAY_EVENTS.md.

## Base verificata

CI verde su e61aa83: backend pytest, migrazioni e frontend completo
(run 39409688398). Giocata e annullamento sponsor sono pubblicati.

## File del blocco

- gift_events.py: card.gifted e card.gift_undone privati al proprietario con
  race_id/gift_id; cards.changed pubblico con soli race_id/pilot_id.
- card_gift.py: evento prima del commit del regalo e prima di eliminare la
  notifica nell'annullo; inventario, pool, notifica ed eventi sono atomici.
  Autorizzazioni, finestra di 60 secondi e controlli sulle giocate invariati.
- test_card_gift_events.py: privacy anche rispetto all'admin, ritorno ai saldi
  iniziali dopo annullo, rifiuti 403/404 senza eventi e rollback dopo flush.

Gli eventi non contengono nomi o immagini delle carte. Il futuro client deve
rileggere le notifiche non viste via API: il replay di card.gifted non autorizza
a mostrare una carta gia' annullata o gia' vista. Il fallback continua a usare
CardGift.seen_at. Nessuna modifica al protocollo delle notifiche persistenti.

## Verifiche e limiti

Servizio e schema CardGiftRead riletti; codici HTTP verificati in api/card_play.py.
Nuovi test non eseguiti localmente: CI del blocco da leggere dopo il push.
Nessuna nuova migrazione, dipendenza, modifica al database reale o immagini.
Nessun backup reale eseguito. Correzioni del revisore ancora da collegare;
frontend SSE e fallback ancora da implementare. Documenti grandi intatti.
