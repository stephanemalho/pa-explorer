"""
Get the most recently generated magic link token from the database.

Usage:
    python scripts/get_magic_link_token.py

Run from the project root directory.
"""
import sqlite3
import os
import sys

DB_PATH = "pa_explorer.db"


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found. Run from project root and start uvicorn first.")
        sys.exit(1)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT token, email, expires_at FROM magic_link_tokens '
            'ORDER BY created_at DESC LIMIT 1'
        )
        row = cursor.fetchone()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        print("The magic_link_tokens table may not exist yet.")
        sys.exit(1)

    if not row:
        print("No magic link tokens found in database.")
        print("Call POST /api/v1/auth/request first to generate one.")
        sys.exit(0)

    token, email, expires_at = row
    print(f"\nLatest magic link token for {email}:")
    print(f"Token: {token}")
    print(f"Expires at: {expires_at}")
    print(f"\nVerify URL: http://localhost:8000/api/v1/auth/verify?token={token}\n")


if __name__ == "__main__":
    main()