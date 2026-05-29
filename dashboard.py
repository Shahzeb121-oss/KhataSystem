# dashboard.py  –  Dashboard tab
import tkinter as tk
from tkinter import ttk
import db

BG   = "#0f1117"
CARD = "#181c27"
ACC  = "#f59e0b"
MUT  = "#64748b"
RED  = "#ef4444"
GRN  = "#22c55e"
BLU  = "#3b82f6"
TXT  = "#e2e8f0"
SOFT = "#1e2435"
FONT = ("Courier", 10)


def _stat_card(parent, icon, label, value, color=TXT):
    f = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1,
                 highlightbackground="#252b3b")
    f.pack(side="left", expand=True, fill="both", padx=6)
    tk.Label(f, text=icon, font=("Segoe UI Emoji", 20), bg=CARD, fg=ACC).pack(pady=(14, 4))
    tk.Label(f, text=label, font=("Courier", 8), bg=CARD, fg=MUT).pack()
    tk.Label(f, text=value, font=("Courier", 14, "bold"), bg=CARD, fg=color).pack(pady=(2, 14))
    return f


class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def refresh(self):
        """Called whenever this tab is switched to."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()

    def _build(self):
        customers = db.get_customers()
        products  = db.get_products()
        sales     = db.get_sales()

        total_credit   = sum(c["balance"] for c in customers)
        total_revenue  = sum(s["total"]   for s in sales)
        pending_count  = sum(1 for s in sales if s["status"] != "paid")

        # ── Title
        tk.Label(self, text="Dashboard", font=("Georgia", 16, "bold"),
                 bg=BG, fg=ACC).pack(anchor="w", padx=28, pady=(20, 4))
        tk.Label(self, text="Welcome back, Admin. Here's your shop summary.",
                 font=FONT, bg=BG, fg=MUT).pack(anchor="w", padx=28, pady=(0, 16))

        # ── Stat row
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=22, pady=(0, 18))
        _stat_card(row, "👥", "Customers",    str(len(customers)))
        _stat_card(row, "📦", "Products",     str(len(products)))
        _stat_card(row, "💸", "Total Credit", f"Rs {total_credit:,.0f}", RED)
        _stat_card(row, "🧾", "Total Sales",  f"Rs {total_revenue:,.0f}", BLU)
        _stat_card(row, "⏳", "Pending Bills",str(pending_count), ACC)

        # ── Two-column lower section
        cols = tk.Frame(self, bg=BG)
        cols.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        # Recent sales
        left = tk.Frame(cols, bg=CARD, bd=0, highlightthickness=1,
                        highlightbackground="#252b3b")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="RECENT SALES", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=14, pady=(12, 8))
        for s in sales[:6]:
            r = tk.Frame(left, bg=SOFT)
            r.pack(fill="x", padx=10, pady=3, ipady=6)
            tk.Label(r, text=s["customer_name"], font=("Courier", 10, "bold"),
                     bg=SOFT, fg=TXT).pack(anchor="w", padx=10)
            tk.Label(r, text=f'{s["product_name"]} × {s["qty"]}',
                     font=("Courier", 8), bg=SOFT, fg=MUT).pack(anchor="w", padx=10)
            tk.Label(r, text=f'Rs {s["total"]:,.0f}', font=("Courier", 10, "bold"),
                     bg=SOFT, fg=ACC).place(relx=1, x=-14, y=6, anchor="ne")

        # Top debtors
        right = tk.Frame(cols, bg=CARD, bd=0, highlightthickness=1,
                         highlightbackground="#252b3b")
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="TOP DEBTORS", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=14, pady=(12, 8))
        debtors = sorted([c for c in customers if c["balance"] > 0],
                         key=lambda c: c["balance"], reverse=True)
        if not debtors:
            tk.Label(right, text="✓ No outstanding balances",
                     font=FONT, bg=CARD, fg=GRN).pack(pady=20)
        for c in debtors[:6]:
            r = tk.Frame(right, bg=SOFT)
            r.pack(fill="x", padx=10, pady=3, ipady=6)
            tk.Label(r, text=c["name"], font=("Courier", 10, "bold"),
                     bg=SOFT, fg=TXT).pack(anchor="w", padx=10)
            tk.Label(r, text=c["phone"], font=("Courier", 8),
                     bg=SOFT, fg=MUT).pack(anchor="w", padx=10)
            tk.Label(r, text=f'Rs {c["balance"]:,.0f}', font=("Courier", 10, "bold"),
                     bg=SOFT, fg=RED).place(relx=1, x=-14, y=6, anchor="ne")
