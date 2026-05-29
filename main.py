# main.py  –  Entry point & main window
import tkinter as tk
from tkinter import ttk

from login     import LoginWindow
from dashboard import DashboardFrame
from customers import CustomersFrame
from products  import ProductsFrame
from sales     import SalesFrame
from reports   import ReportsFrame

BG   = "#0f1117"
CARD = "#181c27"
ACC  = "#f59e0b"
MUT  = "#64748b"
TXT  = "#e2e8f0"
SOFT = "#1e2435"


class MainApp:
    def __init__(self, user):
        self.root = tk.Tk()
        self.root.title("KhataSystem – Shop Credit Ledger")
        self.root.geometry("1100x680")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self._build_sidebar()
        self._build_content()
        self._show_tab("dashboard")
        self.root.mainloop()

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=CARD, width=190, bd=0,
                                highlightthickness=1,
                                highlightbackground="#252b3b")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=CARD)
        logo.pack(fill="x", pady=(20, 18), padx=14)
        tk.Label(logo, text="🏪", font=("Segoe UI Emoji", 28),
                 bg=CARD, fg=ACC).pack()
        tk.Label(logo, text="KhataSystem", font=("Georgia", 13, "bold"),
                 bg=CARD, fg=ACC).pack()
        tk.Label(logo, text="Shop Credit Ledger", font=("Courier", 8),
                 bg=CARD, fg=MUT).pack()
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)

        # Nav buttons
        self.nav_btns = {}
        for key, icon, label in [
            ("dashboard", "📊", "Dashboard"),
            ("customers", "👥", "Customers"),
            ("products",  "📦", "Products"),
            ("sales",     "🧾", "Sales"),
            ("reports",   "📈", "Reports"),
        ]:
            btn = tk.Button(self.sidebar, text=f"  {icon}  {label}",
                            font=("Courier", 10), anchor="w",
                            bg=CARD, fg=MUT, relief="flat", bd=0, cursor="hand2",
                            activebackground=SOFT, activeforeground=ACC,
                            command=lambda k=key: self._show_tab(k))
            btn.pack(fill="x", padx=10, ipady=9, pady=2)
            self.nav_btns[key] = btn

        # Logout at bottom
        tk.Frame(self.sidebar, bg=CARD).pack(expand=True, fill="y")
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)
        tk.Button(self.sidebar, text="  🚪  Logout",
                  font=("Courier", 10), anchor="w",
                  bg=CARD, fg=MUT, relief="flat", bd=0, cursor="hand2",
                  command=self._logout).pack(fill="x", padx=10, ipady=9, pady=(0, 16))

    def _build_content(self):
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.tabs = {
            "dashboard": DashboardFrame(self.content),
            "customers": CustomersFrame(self.content),
            "products":  ProductsFrame(self.content),
            "sales":     SalesFrame(self.content),
            "reports":   ReportsFrame(self.content),
        }
        for frame in self.tabs.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _show_tab(self, key):
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.config(bg=SOFT, fg=ACC, font=("Courier", 10, "bold"))
            else:
                btn.config(bg=CARD, fg=MUT, font=("Courier", 10))

        frame = self.tabs[key]
        frame.lift()
        if hasattr(frame, "refresh"):
            frame.refresh()

    def _logout(self):
        self.root.destroy()
        start()


def start():
    LoginWindow(on_success=lambda user: MainApp(user))


if __name__ == "__main__":
    start()
