# products.py  –  Product Management tab
import tkinter as tk
from tkinter import ttk, messagebox
import db

BG = "#0f1117"; CARD = "#181c27"; ACC = "#f59e0b"
MUT = "#64748b"; RED = "#ef4444"; GRN = "#22c55e"
TXT = "#e2e8f0"; SOFT = "#1e2435"; FONT = ("Courier", 10)
HDR = "#252b3b"

UNITS = ["Kg", "Bag", "Bottle", "Box", "Dozen", "Piece", "Litre", "Gram", "Meter"]


def _lbl_entry(parent, label, var, width=None, **kw):
    tk.Label(parent, text=label, font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(8, 2))
    e = tk.Entry(parent, textvariable=var, font=FONT,
                 bg=SOFT, fg=TXT, insertbackground=ACC, relief="flat", bd=0, **kw)
    e.pack(fill="x", padx=20, ipady=7)


class ProductDialog(tk.Toplevel):
    def __init__(self, parent, product=None, on_save=None):
        super().__init__(parent)
        self.on_save  = on_save
        self.product  = product
        self.title("Edit Product" if product else "Add Product")
        self.geometry("380x400")
        self.configure(bg=CARD)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Edit Product" if product else "Add Product",
                 font=("Georgia", 13, "bold"), bg=CARD, fg=ACC).pack(pady=(18, 4))

        self.name_var  = tk.StringVar(value=product["name"]  if product else "")
        self.price_var = tk.StringVar(value=str(product["price"]) if product else "")
        self.stock_var = tk.StringVar(value=str(product["stock"]) if product else "0")
        self.unit_var  = tk.StringVar(value=product["unit"]  if product else "Kg")

        _lbl_entry(self, "Product Name", self.name_var)
        _lbl_entry(self, "Price (Rs)",   self.price_var)
        _lbl_entry(self, "Stock Qty",    self.stock_var)

        tk.Label(self, text="Unit", font=("Courier", 8), bg=CARD, fg=MUT).pack(anchor="w", padx=20, pady=(8, 2))
        om = ttk.Combobox(self, textvariable=self.unit_var, values=UNITS,
                          font=FONT, state="readonly")
        om.pack(fill="x", padx=20, ipady=4)

        tk.Button(self, text="Save", font=("Courier", 11, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._save).pack(fill="x", padx=20, ipady=8, pady=(18, 4))
        tk.Button(self, text="Cancel", font=FONT,
                  bg=SOFT, fg=MUT, relief="flat", bd=0, cursor="hand2",
                  command=self.destroy).pack(fill="x", padx=20, ipady=6)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.", parent=self); return
        try:
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
        except ValueError:
            messagebox.showerror("Error", "Price and Stock must be numbers.", parent=self); return

        if self.product:
            db.update_product(self.product["product_id"], name, price, stock, self.unit_var.get())
        else:
            db.add_product(name, price, stock, self.unit_var.get())
        if self.on_save:
            self.on_save()
        self.destroy()


class ProductsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self._build()

    def refresh(self):
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(20, 10))
        tk.Label(hdr, text="Products", font=("Georgia", 16, "bold"),
                 bg=BG, fg=ACC).pack(side="left")
        tk.Button(hdr, text="+ Add Product", font=("Courier", 10, "bold"),
                  bg=ACC, fg="#000", relief="flat", bd=0, cursor="hand2",
                  command=self._add).pack(side="right", ipadx=10, ipady=5)

        cols = ("name", "price", "stock", "unit")
        style = ttk.Style()
        style.configure("Prod.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TXT, font=FONT, rowheight=32)
        style.configure("Prod.Treeview.Heading",
                        background=HDR, foreground=MUT, font=("Courier", 9, "bold"))
        style.map("Prod.Treeview", background=[("selected", SOFT)])

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=28, pady=(0, 10))
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings",
                                 style="Prod.Treeview", selectmode="browse")
        for col, txt, w in [("name","Product Name",280),("price","Price (Rs)",130),
                             ("stock","Stock",100),("unit","Unit",100)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=(0, 20))
        tk.Button(bf, text="✏ Edit", font=FONT, bg=SOFT, fg=MUT,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._edit).pack(side="left", padx=(0, 8), ipadx=10, ipady=5)
        tk.Button(bf, text="🗑 Delete", font=FONT, bg="#450a0a", fg=RED,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._delete).pack(side="left", ipadx=10, ipady=5)

        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for p in db.get_products():
            self.tree.insert("", "end", iid=str(p["product_id"]),
                             values=(p["name"], f"Rs {p['price']:,.0f}",
                                     p["stock"], p["unit"]))

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a product first.")
            return None
        pid = int(sel[0])
        return next((p for p in db.get_products() if p["product_id"] == pid), None)

    def _add(self):
        ProductDialog(self, on_save=self._load)

    def _edit(self):
        p = self._selected()
        if p:
            ProductDialog(self, product=p, on_save=self._load)

    def _delete(self):
        p = self._selected()
        if p and messagebox.askyesno("Delete", f"Delete '{p['name']}'?", icon="warning"):
            db.delete_product(p["product_id"])
            self._load()
