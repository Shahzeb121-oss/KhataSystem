#!/usr/bin/env python3
"""
seed_admin.py  –  Creates (or resets) the admin user with a bcrypt-hashed password.
Run this ONCE after importing the SQL schema:
    python3 seed_admin.py
"""
import bcrypt
import mysql.connector
import getpass
import sys

# ── Config ────────────────────────────────────────────────────────────────────
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "Aror@123"   # <-- your MySQL root password
DB_NAME     = "shop_khata"

ADMIN_USERNAME     = "admin"
ADMIN_PASSWORD_RAW = "admin123"   # default; change if you like
# ──────────────────────────────────────────────────────────────────────────────


def main():
    print("=" * 55)
    print("  KhataSystem – Admin Seed Script")
    print("=" * 55)

    # Optionally let user supply a custom password interactively
    use_custom = input("\nSet a custom admin password? (y/N): ").strip().lower()
    if use_custom == "y":
        pw1 = getpass.getpass("  New password   : ")
        pw2 = getpass.getpass("  Confirm        : ")
        if pw1 != pw2:
            print("[ERROR] Passwords do not match. Aborting.")
            sys.exit(1)
        if len(pw1) < 6:
            print("[ERROR] Password must be at least 6 characters.")
            sys.exit(1)
        raw_password = pw1
    else:
        raw_password = ADMIN_PASSWORD_RAW
        print(f"  Using default password: {ADMIN_PASSWORD_RAW}")

    # Hash the password with bcrypt (cost factor 12)
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    print(f"\n  bcrypt hash generated (cost=12) ✔")

    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        cur = conn.cursor()

        # Upsert: insert or update if username already exists
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, 'admin')
            ON DUPLICATE KEY UPDATE password = VALUES(password)
        """, (ADMIN_USERNAME, hashed))
        conn.commit()
        cur.close()
        conn.close()

        print(f"  Admin user '{ADMIN_USERNAME}' saved to database ✔")
        print(f"\n  Login credentials:")
        print(f"    Username : {ADMIN_USERNAME}")
        print(f"    Password : {raw_password}")
        print("\n  Done. You can now run:  python3 main.py")

    except mysql.connector.Error as e:
        print(f"\n[DB ERROR] {e}")
        print("Check your DB_PASSWORD and DB_HOST in seed_admin.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
