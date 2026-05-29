# reports.py  –  Reports & Analytics tab
import tkinter as tk
from tkinter import ttk
import db

BG = "#0f1117"; CARD = "#181c27"; ACC = "#f59e0b"
MUT = "#64748b"; RED = "#ef4444"; GRN = "#22c55e"
BLU = "#3b82f6"; TXT = "#e2e8f0"; SOFT = "#1e2435"
FONT = ("Courier", 10); HDR = "#252b3b"

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class ReportsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.period = tk.StringVar(value="all")
        self._build()

    def refresh(self):
        self._reload()

    def _build(self):
        # Header + period selector
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(20, 10))
        tk.Label(hdr, text="Reports & Analytics", font=("Georgia", 16, "bold"),
                 bg=BG, fg=ACC).pack(side="left")
        for p, lbl in [("today","Today"),("week","Week"),("month","Month"),("all","All Time")]:
            tk.Radiobutton(hdr, text=lbl, variable=self.period, value=p,
                           font=("Courier", 9), bg=BG, fg=MUT, selectcolor=SOFT,
                           activebackground=BG, activeforeground=ACC,
                           command=self._reload).pack(side="right", padx=4)

        # Stat row
        self.stat_frame = tk.Frame(self, bg=BG)
        self.stat_frame.pack(fill="x", padx=22, pady=(0, 16))

        # Two-col middle
        mid = tk.Frame(self, bg=BG)
        mid.pack(fill="both", expand=True, padx=22, pady=(0, 10))

        self.chart_frame  = tk.Frame(mid, bg=CARD, highlightthickness=1,
                                     highlightbackground="#252b3b")
        self.chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.prod_frame   = tk.Frame(mid, bg=CARD, highlightthickness=1,
                                     highlightbackground="#252b3b")
        self.prod_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # Ledger table
        self.ledger_frame = tk.Frame(self, bg=CARD, highlightthickness=1,
                                     highlightbackground="#252b3b")
        self.ledger_frame.pack(fill="x", padx=22, pady=(0, 20))

        self._reload()

    def _reload(self):
        summary, by_cust, by_prod, ledger = db.report_summary(self.period.get())

        revenue   = float(summary.get("revenue")   or 0)
        collected = float(summary.get("collected") or 0)
        pending   = revenue - collected
        credit    = sum(float(r["balance"]) for r in ledger)

        # Stat cards
        for w in self.stat_frame.winfo_children():
            w.destroy()
        for icon, lbl, val, col in [
            ("💰", "Revenue",   f"Rs {revenue:,.0f}",   BLU),
            ("✅", "Collected", f"Rs {collected:,.0f}", GRN),
            ("⏳", "Pending",   f"Rs {pending:,.0f}",   ACC),
            ("🔴", "Credit",    f"Rs {credit:,.0f}",    RED),
        ]:
            f = tk.Frame(self.stat_frame, bg=CARD, bd=0,
                         highlightthickness=1, highlightbackground="#252b3b")
            f.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(f, text=icon, font=("Segoe UI Emoji", 18), bg=CARD, fg=ACC).pack(pady=(12, 2))
            tk.Label(f, text=lbl, font=("Courier", 8), bg=CARD, fg=MUT).pack()
            tk.Label(f, text=val, font=("Courier", 12, "bold"), bg=CARD, fg=col).pack(pady=(2, 12))

        # Bar chart (customers)
        for w in self.chart_frame.winfo_children():
            w.destroy()
        tk.Label(self.chart_frame, text="SALES BY CUSTOMER",
                 font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=14, pady=(12, 6))
        if HAS_MPL and by_cust:
            self._draw_bar(self.chart_frame,
                           [r["name"].split()[0] for r in by_cust[:6]],
                           [float(r["total"]) for r in by_cust[:6]],
                           ACC)
        else:
            max_v = max((float(r["total"]) for r in by_cust), default=1)
            for r in by_cust[:6]:
                self._bar_row(self.chart_frame, r["name"],
                              float(r["total"]), max_v, ACC)

        # Bar chart (products)
        for w in self.prod_frame.winfo_children():
            w.destroy()
        tk.Label(self.prod_frame, text="TOP PRODUCTS",
                 font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=14, pady=(12, 6))
        if HAS_MPL and by_prod:
            self._draw_bar(self.prod_frame,
                           [r["name"].split()[0] for r in by_prod[:6]],
                           [float(r["revenue"]) for r in by_prod[:6]],
                           BLU)
        else:
            max_v = max((float(r["revenue"]) for r in by_prod), default=1)
            for r in by_prod[:6]:
                self._bar_row(self.prod_frame, r["name"],
                              float(r["revenue"]), max_v, BLU)

        # Credit ledger table
        for w in self.ledger_frame.winfo_children():
            w.destroy()
        tk.Label(self.ledger_frame, text="CREDIT LEDGER — OUTSTANDING BALANCES",
                 font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=14, pady=(12, 6))

        style = ttk.Style()
        style.configure("Led.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TXT, font=FONT, rowheight=28)
        style.configure("Led.Treeview.Heading",
                        background=HDR, foreground=MUT, font=("Courier", 9, "bold"))
        style.map("Led.Treeview", background=[("selected", SOFT)])

        cols = ("name", "phone", "balance")
        tree = ttk.Treeview(self.ledger_frame, columns=cols, show="headings",
                            style="Led.Treeview", height=4)
        for col, txt, w in [("name","Customer",220),("phone","Phone",140),
                             ("balance","Balance Due",140)]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="w")
        for r in ledger:
            tree.insert("", "end", values=(r["name"], r["phone"] or "",
                                           f"Rs {float(r['balance']):,.0f}"))
        tree.pack(fill="x", padx=10, pady=(0, 12))

    def _bar_row(self, parent, label, value, max_val, color):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", padx=14, pady=3)
        tk.Label(f, text=label[:20], font=("Courier", 9), bg=CARD, fg=TXT, width=20, anchor="w").pack(side="left")
        bar_w = int((value / max_val) * 160) if max_val else 0
        bar = tk.Frame(f, bg=color, height=14, width=bar_w)
        bar.pack(side="left", padx=4)
        tk.Label(f, text=f"Rs {value:,.0f}", font=("Courier", 8), bg=CARD, fg=color).pack(side="left")

    def _draw_bar(self, parent, labels, values, color):
        hex_to_01 = lambda h: tuple(int(h[i:i+2], 16)/255 for i in (1, 3, 5))
        fig, ax = plt.subplots(figsize=(3.4, 2.4), facecolor="#181c27")
        ax.set_facecolor("#181c27")
        bars = ax.bar(labels, values, color=color, width=0.5)
        ax.tick_params(colors="#64748b", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#252b3b")
        ax.yaxis.set_tick_params(labelcolor="#64748b")
        fig.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 10))
        plt.close(fig)
