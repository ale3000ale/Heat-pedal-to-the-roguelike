from sqlalchemy import select

from app.db.models import DeckPrototype
from app.db.session import SessionLocal

PROTOTYPE_NAME = "default"


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(DeckPrototype).where(DeckPrototype.name == PROTOTYPE_NAME)):
            print(f"Prototipo '{PROTOTYPE_NAME}' già presente. Nessuna modifica.")
            return
        db.add(DeckPrototype(name=PROTOTYPE_NAME, base_cards="[]"))
        db.commit()
        print(f"Prototipo '{PROTOTYPE_NAME}' creato (pool vuota).")


if __name__ == "__main__":
    main()