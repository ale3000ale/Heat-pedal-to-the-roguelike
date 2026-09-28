# Bozza dei Requisiti

## Decisioni definitive

- possono esistere più campionati attivi contemporaneamente;
- la cronologia dei campionati chiusi deve essere mantenuta;

## Relazioni definitive

- User 1:N Team
- User 1:N Pilot
- Team 1:N Pilot
- Pilot 1:1 Deck
- Championship 1:N ChampionshipPilot
- ChampionshipPilot N:1 Pilot
- Championship 1:N Race
- Race 1:N RaceResult
- Pilot 1:N RaceResult
- DeckPrototype (indipendente; usato solo come sorgente per reset/creazione mazzi)
