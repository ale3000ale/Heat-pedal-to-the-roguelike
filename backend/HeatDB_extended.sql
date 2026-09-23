-- HeatDB_extended.sql
-- Schema esteso a partire da HeatDB.sql originale.
-- Estensioni: role su User, ChampionshipParticipant (storico punti per campionato),
-- pilot_id su Deck, ShopItem, Purchase.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "User" (
  "id" INTEGER NOT NULL,
  "username" TEXT NOT NULL UNIQUE,
  "password" TEXT NOT NULL,          -- hash bcrypt, non password in chiaro
  "role" TEXT NOT NULL DEFAULT 'user', -- 'user' | 'admin'
  "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Team" (
  "id" INTEGER NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Championship" (
  "id" INTEGER NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  "pilots" TEXT,                     -- mantenuto per retrocompatibilita' (denormalizzato, non usato in logica)
  "deck" INTEGER,                    -- deck "ufficiale" del campionato (opzionale)
  "date" DATETIME NOT NULL,
  PRIMARY KEY("id"),
  FOREIGN KEY ("deck") REFERENCES "Deck"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS "Pilot" (
  "id" INTEGER NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  "gold" INTEGER NOT NULL DEFAULT 0,
  "sponsor" INTEGER NOT NULL DEFAULT 0,
  "point" INTEGER NOT NULL DEFAULT 0,
  "championship_id" INTEGER,
  "team" INTEGER,
  "user_id" INTEGER NOT NULL,
  PRIMARY KEY("id"),
  FOREIGN KEY ("team") REFERENCES "Team"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION,
  FOREIGN KEY ("championship_id") REFERENCES "Championship"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION,
  FOREIGN KEY ("user_id") REFERENCES "User"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS "Deck_prototype" (
  "id" INTEGER NOT NULL,
  "base_cards" TEXT,                 -- JSON: array di {path, value}
  "name" TEXT NOT NULL UNIQUE,
  PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Deck" (
  "id" INTEGER NOT NULL,
  "cards" TEXT,                      -- JSON: array di {path, value}
  "id_prototype" INTEGER NOT NULL,
  "pilot_id" INTEGER,                -- NEW: mazzo concreto assegnato a un pilota
  PRIMARY KEY("id"),
  FOREIGN KEY ("id_prototype") REFERENCES "Deck_prototype"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION,
  FOREIGN KEY ("pilot_id") REFERENCES "Pilot"("id")
    ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- NEW: storico punti/ranking di un pilota per un dato campionato
CREATE TABLE IF NOT EXISTS "ChampionshipParticipant" (
  "id" INTEGER NOT NULL,
  "championship_id" INTEGER NOT NULL,
  "pilot_id" INTEGER NOT NULL,
  "points" INTEGER NOT NULL DEFAULT 0,
  "ranking" INTEGER,
  PRIMARY KEY("id"),
  UNIQUE("championship_id", "pilot_id"),
  FOREIGN KEY ("championship_id") REFERENCES "Championship"("id")
    ON UPDATE NO ACTION ON DELETE CASCADE,
  FOREIGN KEY ("pilot_id") REFERENCES "Pilot"("id")
    ON UPDATE NO ACTION ON DELETE CASCADE
);

-- NEW: oggetti acquistabili nel negozio, legati a un campionato
CREATE TABLE IF NOT EXISTS "ShopItem" (
  "id" INTEGER NOT NULL,
  "championship_id" INTEGER NOT NULL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "price_gold" INTEGER NOT NULL DEFAULT 0,
  "price_points" INTEGER NOT NULL DEFAULT 0,
  "requirements" TEXT,               -- testo libero / JSON requisiti
  "image_path" TEXT,
  PRIMARY KEY("id"),
  FOREIGN KEY ("championship_id") REFERENCES "Championship"("id")
    ON UPDATE NO ACTION ON DELETE CASCADE
);

-- NEW: storico acquisti
CREATE TABLE IF NOT EXISTS "Purchase" (
  "id" INTEGER NOT NULL,
  "user_id" INTEGER NOT NULL,
  "pilot_id" INTEGER NOT NULL,
  "championship_id" INTEGER NOT NULL,
  "item_id" INTEGER NOT NULL,
  "purchased_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY("id"),
  FOREIGN KEY ("user_id") REFERENCES "User"("id"),
  FOREIGN KEY ("pilot_id") REFERENCES "Pilot"("id"),
  FOREIGN KEY ("championship_id") REFERENCES "Championship"("id"),
  FOREIGN KEY ("item_id") REFERENCES "ShopItem"("id")
);
