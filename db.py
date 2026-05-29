# db.py  –  Database connection & helper queries
# FIXED: verify_login now uses bcrypt.checkpw() instead of plain-text SQL comparison.
import mysql.connector
from mysql.connector import Error
import bcrypt

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "Aror@123",   # <-- set your MySQL password here
    "database": "shop_khata",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def execute(query, params=(), fetch=False):
    """Run a query; return rows if fetch=True, else lastrowid."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"[DB ERROR] {e}")
        return [] if fetch else None
    finally:
        conn.close()


# ── Auth ──────────────────────────────────────────────────────────────────────
def verify_login(username, password):
    """
    BUG FIX: The original code did:
        SELECT * FROM users WHERE username=%s AND password=%s
    This compared the plain-text input against whatever is stored in the DB.

    If the DB contains a bcrypt hash (which it SHOULD for security), this
    comparison always fails because 'admin123' != '$2b$12$...'.

    Fix: fetch the row by username only, then use bcrypt.checkpw() to
    verify the password against the stored hash.
    """
    rows = execute(
        "SELECT * FROM users WHERE username=%s",
        (username,), fetch=True
    )
    if not rows:
        return None

    user = rows[0]
    stored_hash = user.get("password", "")

    # Guard: handle legacy plain-text passwords (migration path)
    if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
        # bcrypt hash in DB — use secure comparison
        try:
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                return user
        except Exception as e:
            print(f"[AUTH ERROR] bcrypt check failed: {e}")
        return None
    else:
        # Plain-text stored (legacy / first-run before seed script) — direct compare
        # TODO: migrate this user's password to bcrypt after successful login
        if stored_hash == password:
            _migrate_password_to_bcrypt(user["user_id"], password)
            return user
        return None


def _migrate_password_to_bcrypt(user_id, raw_password):
    """Silently upgrades a plain-text password to bcrypt on first login."""
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    execute(
        "UPDATE users SET password=%s WHERE user_id=%s",
        (hashed, user_id)
    )
    print(f"[AUTH] Password for user_id={user_id} migrated to bcrypt ✔")


# ── Customers ─────────────────────────────────────────────────────────────────
def get_customers(search=""):
    if search:
        return execute(
            "SELECT * FROM customers WHERE name LIKE %s OR phone LIKE %s ORDER BY name",
            (f"%{search}%", f"%{search}%"), fetch=True
        )
    return execute("SELECT * FROM customers ORDER BY name", fetch=True)

def add_customer(name, phone, address):
    return execute(
        "INSERT INTO customers (name, phone, address) VALUES (%s,%s,%s)",
        (name, phone, address)
    )

def update_customer(customer_id, name, phone, address):
    execute(
        "UPDATE customers SET name=%s, phone=%s, address=%s WHERE customer_id=%s",
        (name, phone, address, customer_id)
    )

def delete_customer(customer_id):
    execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))

def update_balance(customer_id, amount):
    execute(
        "UPDATE customers SET balance = GREATEST(0, balance - %s) WHERE customer_id=%s",
        (amount, customer_id)
    )

def increase_balance(customer_id, amount):
    execute(
        "UPDATE customers SET balance = balance + %s WHERE customer_id=%s",
        (amount, customer_id)
    )


# ── Products ──────────────────────────────────────────────────────────────────
def get_products():
    return execute("SELECT * FROM products ORDER BY name", fetch=True)

def add_product(name, price, stock, unit):
    return execute(
        "INSERT INTO products (name, price, stock, unit) VALUES (%s,%s,%s,%s)",
        (name, price, stock, unit)
    )

def update_product(product_id, name, price, stock, unit):
    execute(
        "UPDATE products SET name=%s, price=%s, stock=%s, unit=%s WHERE product_id=%s",
        (name, price, stock, unit, product_id)
    )

def delete_product(product_id):
    execute("DELETE FROM products WHERE product_id=%s", (product_id,))

def reduce_stock(product_id, qty):
    execute(
        "UPDATE products SET stock = GREATEST(0, stock - %s) WHERE product_id=%s",
        (qty, product_id)
    )


# ── Sales ─────────────────────────────────────────────────────────────────────
def get_sales(search=""):
    q = """
        SELECT s.*, c.name AS customer_name, p.name AS product_name
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN products  p ON s.product_id  = p.product_id
    """
    if search:
        q += " WHERE c.name LIKE %s OR p.name LIKE %s"
        q += " ORDER BY s.sale_id DESC"
        return execute(q, (f"%{search}%", f"%{search}%"), fetch=True)
    return execute(q + " ORDER BY s.sale_id DESC", fetch=True)

def add_sale(customer_id, product_id, qty, price, total, paid, status, sale_date):
    return execute(
        """INSERT INTO sales
           (customer_id, product_id, qty, price, total, paid, status, sale_date)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (customer_id, product_id, qty, price, total, paid, status, sale_date)
    )

def mark_sale_paid(sale_id):
    execute(
        "UPDATE sales SET paid=total, status='paid' WHERE sale_id=%s",
        (sale_id,)
    )

def delete_sale(sale_id):
    execute("DELETE FROM sales WHERE sale_id=%s", (sale_id,))


# ── Reports ───────────────────────────────────────────────────────────────────
def report_summary(period="all"):
    where = {
        "today": "WHERE s.sale_date = CURDATE()",
        "week":  "WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)",
        "month": "WHERE MONTH(s.sale_date)=MONTH(CURDATE()) AND YEAR(s.sale_date)=YEAR(CURDATE())",
        "all":   "",
    }.get(period, "")

    totals = execute(
        f"SELECT SUM(total) AS revenue, SUM(paid) AS collected FROM sales {where}",
        fetch=True
    )
    by_customer = execute(
        f"""SELECT c.name, SUM(s.total) AS total, SUM(s.paid) AS paid
            FROM sales s JOIN customers c ON s.customer_id=c.customer_id {where}
            GROUP BY c.customer_id ORDER BY total DESC""",
        fetch=True
    )
    by_product = execute(
        f"""SELECT p.name, SUM(s.qty) AS qty, SUM(s.total) AS revenue
            FROM sales s JOIN products p ON s.product_id=p.product_id {where}
            GROUP BY p.product_id ORDER BY revenue DESC""",
        fetch=True
    )
    credit_ledger = execute(
        "SELECT name, phone, balance FROM customers ORDER BY balance DESC",
        fetch=True
    )
    return totals[0] if totals else {}, by_customer, by_product, credit_ledger
