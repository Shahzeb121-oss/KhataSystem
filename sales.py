# sales.py  –  Sales Module tab
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import db

BG = "#0f1117"; CARD = "#181c27"; ACC = "#f59e0b"
MUT = "#64748b"; RED = "#ef4444"; GRN = "#22c55e"
TXT = "#e2e8f0"; SOFT = "#1e2435"; FONT = ("Courier", 10)
HDR = "#252b3b"


class SaleDialog(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Record New Sale")
        self.geometry("420x540")
        self.configure(bg=CARD)
        self.resizable(False, False)
        self.grab_set()

        self.customers = db.get_customers()
        self.products  = db.get_products()

        tk.Label(self, text="Record New Sale", font=("Georgia", 13, "bold"),
                 bg=CARD, fg=ACC).pack(pady=(18, 4))

        # Customer
        tk.Label(self, text="Customer", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(10, 2))
        self.cust_var = tk.StringVar()
        cust_names = [c["name"] for c in self.customers]
        self.cust_cb = ttk.Combobox(self, textvariable=self.cust_var,
                                    values=cust_names, font=FONT, state="readonly")
        self.cust_cb.pack(fill="x", padx=20, ipady=4)

        # Product
        tk.Label(self, text="Product", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(10, 2))
        self.prod_var = tk.StringVar()
        prod_labels   = [f"{p['name']}  (Rs {p['price']:,.0f})" for p in self.products]
        self.prod_cb  = ttk.Combobox(self, textvariable=self.prod_var,
                                     values=prod_labels, font=FONT, state="readonly")
        self.prod_cb.pack(fill="x", padx=20, ipady=4)
        self.prod_cb.bind("<<ComboboxSelected>>", self._update_total)

        # Qty & Paid
        row = tk.Frame(self, bg=CARD)
        row.pack(fill="x", padx=20, pady=(10, 0))
        for label, attr in [("Quantity", "qty_var"), ("Amount Paid (Rs)", "paid_var")]:
            col = tk.Frame(row, bg=CARD)
            col.pack(side="left", expand=True, fill="x", padx=(0, 6))
            tk.Label(col, text=label, font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", pady=(0, 2))
            var = tk.StringVar(value="1" if "qty" in attr else "0")
            setattr(self, attr, var)
            var.trace_add("write", lambda *_: self._update_total())
            tk.Entry(col, textvariable=var, font=FONT,
                     bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0).pack(fill="x", ipady=7)

        # Date
        tk.Label(self, text="Date (YYYY-MM-DD)", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(10, 2))
        self.date_var = tk.StringVar(value=str(date.today()))
        tk.Entry(self, textvariable=self.date_var, font=FONT,
                 bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0).pack(fill="x", padx=20, ipady=7)

        # Summary card
        self.summary = tk.Frame(self, bg=SOFT, bd=0)
        self.summary.pack(fill="x", padx=20, pady=14)
        self.total_lbl  = tk.Label(self.summary, text="Total:     Rs 0", font=FONT, bg=SOFT, fg=TXT)
        self.total_lbl.pack(anchor="w", padx=12, pady=(8, 2))
        self.remain_lbl = tk.Label(self.summary, text="Remaining: Rs 0", font=FONT, bg=SOFT, fg=RED)
        self.remain_lbl.pack(anchor="w", padx=12, pady=(0, 2))
        self.status_lbl = tk.Label(self.summary, text="Status: credit", font=("Courier", 9), bg=SOFT, fg=MUT)
        self.status_lbl.pack(anchor="w", padx=12, pady=(0, 8))

        tk.Button(self, text="Record Sale", font=("Courier", 11, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._save).pack(fill="x", padx=20, ipady=8, pady=(4, 4))
        tk.Button(self, text="Cancel", font=FONT,
                  bg=SOFT, fg=MUT, relief="flat", bd=0, cursor="hand2",
                  command=self.destroy).pack(fill="x", padx=20, ipady=6)

    def _selected_product(self):
        idx = self.prod_cb.current()
        return self.products[idx] if idx >= 0 else None

    def _update_total(self, *_):
        p = self._selected_product()
        if not p:
            return
        try:
            qty  = int(self.qty_var.get() or 0)
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            return
        total = p["price"] * qty
        remain= max(0, total - paid)
        status= "paid" if paid >= total else ("partial" if paid > 0 else "credit")
        self.total_lbl.config( text=f"Total:     Rs {total:,.0f}")
        self.remain_lbl.config(text=f"Remaining: Rs {remain:,.0f}",
                               fg=RED if remain > 0 else GRN)
        self.status_lbl.config(text=f"Status: {status}")

    def _save(self):
        cidx = self.cust_cb.current()
        pidx = self.prod_cb.current()
        if cidx < 0 or pidx < 0:
            messagebox.showerror("Error", "Select a customer and product.", parent=self); return
        try:
            qty  = int(self.qty_var.get())
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Quantity and paid amount must be numbers.", parent=self); return

        customer = self.customers[cidx]
        product  = self.products[pidx]
        total    = product["price"] * qty
        remain   = total - paid
        status   = "paid" if paid >= total else ("partial" if paid > 0 else "credit")

        db.add_sale(customer["customer_id"], product["product_id"],
                    qty, product["price"], total, paid, status, self.date_var.get())
        db.reduce_stock(product["product_id"], qty)
        if remain > 0:
            db.increase_balance(customer["customer_id"], remain)

        if self.on_save:
            self.on_save()
        self.destroy()


class SalesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def refresh(self):
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(20, 10))
        tk.Label(hdr, text="Sales", font=("Georgia", 16, "bold"),
                 bg=BG, fg=ACC).pack(side="left")
        tk.Button(hdr, text="+ New Sale", font=("Courier", 10, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._new).pack(side="right", ipadx=10, ipady=5)

        # Search
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 10))
        tk.Label(sf, text="Search:", font=FONT, bg=BG, fg=MUT).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        tk.Entry(sf, textvariable=self.search_var, font=FONT,
                 bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0,
                 width=30).pack(side="left", ipady=6)

        cols = ("date", "customer", "product", "qty", "total", "paid", "status")
        style = ttk.Style()
        style.configure("Sale.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TXT, font=FONT, rowheight=32)
        style.configure("Sale.Treeview.Heading",
                        background=HDR, foreground=MUT, font=("Courier", 9, "bold"))
        style.map("Sale.Treeview", background=[("selected", SOFT)])

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=28, pady=(0, 10))
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings",
                                 style="Sale.Treeview", selectmode="browse")
        for col, txt, w in [("date","Date",90),("customer","Customer",160),
                             ("product","Product",160),("qty","Qty",50),
                             ("total","Total",110),("paid","Paid",110),
                             ("status","Status",80)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=(0, 20))
        tk.Button(bf, text="✅ Mark Paid", font=FONT, bg="#052e16", fg=GRN,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._mark_paid).pack(side="left", padx=(0, 8), ipadx=10, ipady=5)
        tk.Button(bf, text="🗑 Delete Sale", font=FONT, bg="#450a0a", fg=RED,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._delete).pack(side="left", ipadx=10, ipady=5)

        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for s in db.get_sales(self.search_var.get()):
            self.tree.insert("", "end", iid=str(s["sale_id"]),
                             values=(s["sale_date"], s["customer_name"],
                                     s["product_name"], s["qty"],
                                     f"Rs {s['total']:,.0f}",
                                     f"Rs {s['paid']:,.0f}",
                                     s["status"].upper()))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a sale first.")
            return None
        return int(sel[0])

    def _new(self):
        SaleDialog(self, on_save=self._load)

    def _mark_paid(self):
        sid = self._selected_id()
        if sid is None:
            return
        sale = next((s for s in db.get_sales() if s["sale_id"] == sid), None)
        if sale and sale["status"] == "paid":
            messagebox.showinfo("Info", "This sale is already marked as paid."); return
        if sale and messagebox.askyesno("Confirm", "Mark this sale as fully paid?"):
            remaining = sale["total"] - sale["paid"]
            db.mark_sale_paid(sid)
            db.update_balance(sale["customer_id"], remaining)
            self._load()

    def _delete(self):
        sid = self._selected_id()
        if sid is None:
            return
        sale = next((s for s in db.get_sales() if s["sale_id"] == sid), None)
        if sale and messagebox.askyesno("Delete", "Delete this sale record?", icon="warning"):
            if sale["status"] != "paid":
                db.update_balance(sale["customer_id"], -(sale["total"] - sale["paid"]))
            db.delete_sale(sid)
            self._load()
