import os
from getpass import getpass

from sqlalchemy import select

from app.db.models import User
from app.db.session import SessionLocal
from app.security import hash_password


def main() -> None:
    username = os.environ.get("HEAT_ADMIN_USERNAME") or input("Username admin: ").strip().lower()
    password = os.environ.get("HEAT_ADMIN_PASSWORD") or getpass("Password admin: ")

    if not username or not password:
        raise SystemExit("Username e password sono obbligatori.")

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.role == "admin"))
        if existing is not None:
            print(f"Esiste già un admin ('{existing.username}'). Nessuna modifica.")
            return
        if db.scalar(select(User).where(User.username == username)) is not None:
            raise SystemExit(f"Lo username '{username}' è già in uso.")
        db.add(User(username=username, password=hash_password(password), role="admin"))
        db.commit()
        print(f"Admin '{username}' creato.")


if __name__ == "__main__":
    main()