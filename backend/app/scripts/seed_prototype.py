from sqlalchemy import select

from app.db.models import DeckPrototype
from app.db.session import SessionLocal
from app.services.pools import BASE_POOL_NAMES


def main() -> None:
    # Crea le pool di base mancanti (modifiche e sponsor), vuote: si riempiono con la ricarica.
    with SessionLocal() as db:
        for kind, name in BASE_POOL_NAMES.items():
            if db.scalar(select(DeckPrototype).where(DeckPrototype.name == name)):
                print(f"Pool di base '{name}' ({kind}) già presente. Nessuna modifica.")
                continue
            db.add(DeckPrototype(name=name, base_cards="[]", kind=kind))
            db.commit()
            print(f"Pool di base '{name}' ({kind}) creata (vuota).")


if __name__ == "__main__":
    main()
