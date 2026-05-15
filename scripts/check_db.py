"""
Diagnostic script for the PA-Explorer SQLite database.

Lists all tables and shows the row count for each.
Optionally displays the content of small reference tables
like user_allowlist.

Usage:
    python scripts/check_db.py
"""
import sqlite3

DB_PATH = "pa_explorer.db"

# Tables whose content we want to display in full
REFERENCE_TABLES = ["user_allowlist"]


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lister toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nBase: {DB_PATH}")
    print(f"Tables trouvees: {len(tables)}\n")

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} ligne(s)")

    # Afficher le contenu des tables de référence
    for ref_table in REFERENCE_TABLES:
        if ref_table in tables:
            cursor.execute(f"SELECT * FROM {ref_table}")
            rows = cursor.fetchall()
            if rows:
                print(f"\nContenu de {ref_table}:")
                for row in rows:
                    print(f"  {row}")

    conn.close()
    print()


if __name__ == "__main__":
    main()