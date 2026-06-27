"""
Peuple la table user_allowlist avec l'email admin initial.

Doit être exécuté une fois après alembic upgrade head, et après toute
réinitialisation de la base. Idempotent : sans effet si l'email est
déjà présent.

Usage:
    python scripts/seed_db.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import SessionLocal
from app.models.user_allowlist import UserAllowlist


def main():
    email = settings.pa_explorer_initial_admin_email
    db = SessionLocal()
    try:
        exists = db.query(UserAllowlist).filter(UserAllowlist.email == email).first()
        if exists:
            print(f"Allowlist : {email} déjà présent — aucune modification.")
        else:
            db.add(UserAllowlist(email=email))
            db.commit()
            print(f"Allowlist : {email} ajouté.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
