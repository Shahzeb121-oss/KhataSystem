# customers.py  –  Customer Management tab
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db

BG = "#0f1117"; CARD = "#181c27"; ACC = "#f59e0b"
MUT = "#64748b"; RED = "#ef4444"; GRN = "#22c55e"
TXT = "#e2e8f0"; SOFT = "#1e2435"; FONT = ("Courier", 10)
HDR = "#252b3b"


def _entry_row(parent, label, var, show=""):
    tk.Label(parent, text=label, font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(8, 2))
    e = tk.Entry(parent, textvariable=var, show=show, font=FONT,
                 bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0)
    e.pack(fill="x", padx=20, ipady=7)
    return e


class CustomerDialog(tk.Toplevel):
    def __init__(self, parent, customer=None, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.customer = customer
        self.title("Edit Customer" if customer else "Add Customer")
        self.geometry("380x340")
        self.configure(bg=CARD)
        self.resizable(False, False)
        self.grab_set()

        title = "Edit Customer" if customer else "Add Customer"
        tk.Label(self, text=title, font=("Georgia", 13, "bold"),
                 bg=CARD, fg=ACC).pack(pady=(18, 4))

        self.name_var = tk.StringVar(value=customer["name"]    if customer else "")
        self.phone_var= tk.StringVar(value=customer["phone"]   if customer else "")
        self.addr_var = tk.StringVar(value=customer["address"] if customer else "")

        _entry_row(self, "Name",    self.name_var)
        _entry_row(self, "Phone",   self.phone_var)
        _entry_row(self, "Address", self.addr_var)

        tk.Button(self, text="Save", font=("Courier", 11, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._save).pack(fill="x", padx=20, ipady=8, pady=(18, 4))
        tk.Button(self, text="Cancel", font=FONT,
                  bg=SOFT, fg=MUT, relief="flat", bd=0, cursor="hand2",
                  command=self.destroy).pack(fill="x", padx=20, ipady=6)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.", parent=self)
            return
        if self.customer:
            db.update_customer(self.customer["customer_id"],
                               name, self.phone_var.get(), self.addr_var.get())
        else:
            db.add_customer(name, self.phone_var.get(), self.addr_var.get())
        if self.on_save:
            self.on_save()
        self.destroy()


class CustomersFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def refresh(self):
        self._load()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(20, 10))
        tk.Label(hdr, text="Customers", font=("Georgia", 16, "bold"),
                 bg=BG, fg=ACC).pack(side="left")
        tk.Button(hdr, text="+ Add Customer", font=("Courier", 10, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._add).pack(side="right", padx=4, ipadx=10, ipady=5)

        # Search
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 10))
        tk.Label(sf, text="Search:", font=FONT, bg=BG, fg=MUT).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        tk.Entry(sf, textvariable=self.search_var, font=FONT,
                 bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0,
                 width=30).pack(side="left", ipady=6)

        # Treeview
        cols = ("name", "phone", "address", "balance", "actions")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Khata.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TXT, font=FONT, rowheight=32)
        style.configure("Khata.Treeview.Heading",
                        background=HDR, foreground=MUT, font=("Courier", 9, "bold"))
        style.map("Khata.Treeview", background=[("selected", SOFT)])

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings",
                                 style="Khata.Treeview", selectmode="browse")
        headers = {"name": ("Name", 180), "phone": ("Phone", 130),
                   "address": ("Address", 200), "balance": ("Balance (Rs)", 120),
                   "actions": ("Actions", 180)}
        for col, (txt, w) in headers.items():
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Button panel below tree
        self.btn_frame = tk.Frame(self, bg=BG)
        self.btn_frame.pack(fill="x", padx=28, pady=(0, 10))
        tk.Button(self.btn_frame, text="✏ Edit Selected", font=FONT,
                  bg=SOFT, fg=MUT, relief="flat", bd=0, cursor="hand2",
                  command=self._edit).pack(side="left", padx=(0, 8), ipadx=10, ipady=5)
        tk.Button(self.btn_frame, text="💚 Receive Payment", font=FONT,
                  bg="#052e16", fg=GRN, relief="flat", bd=0, cursor="hand2",
                  command=self._pay).pack(side="left", padx=(0, 8), ipadx=10, ipady=5)
        tk.Button(self.btn_frame, text="🗑 Delete", font=FONT,
                  bg="#450a0a", fg=RED, relief="flat", bd=0, cursor="hand2",
                  command=self._delete).pack(side="left", ipadx=10, ipady=5)

        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for c in db.get_customers(self.search_var.get()):
            bal = f"Rs {c['balance']:,.0f}"
            self.tree.insert("", "end", iid=str(c["customer_id"]),
                             values=(c["name"], c["phone"] or "", c["address"] or "",
                                     bal, "select to act"))

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a customer first.")
            return None
        cid = int(sel[0])
        rows = db.get_customers()
        return next((c for c in rows if c["customer_id"] == cid), None)

    def _add(self):
        CustomerDialog(self, on_save=self._load)

    def _edit(self):
        c = self._selected()
        if c:
            CustomerDialog(self, customer=c, on_save=self._load)

    def _pay(self):
        c = self._selected()
        if not c:
            return
        if c["balance"] <= 0:
            messagebox.showinfo("Info", f"{c['name']} has no outstanding balance.")
            return
        amt = simpledialog.askfloat("Receive Payment",
                                    f"Outstanding: Rs {c['balance']:,.0f}\n\nEnter payment amount:",
                                    parent=self, minvalue=1)
        if amt:
            db.update_balance(c["customer_id"], amt)
            self._load()

    def _delete(self):
        c = self._selected()
        if c and messagebox.askyesno("Delete",
                f"Delete {c['name']} and all their sales?", icon="warning"):
            db.delete_customer(c["customer_id"])
            self._load()
