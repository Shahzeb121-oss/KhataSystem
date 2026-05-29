# login.py  –  Login screen
import tkinter as tk
from tkinter import messagebox
import db


class LoginWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = tk.Tk()
        self.root.title("KhataSystem – Login")
        self.root.geometry("400x460")
        self.root.configure(bg="#0f1117")
        self.root.resizable(False, False)
        self._center()
        self._build()
        self.root.mainloop()

    def _center(self):
        self.root.update_idletasks()
        w, h = 400, 460
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        frame = tk.Frame(self.root, bg="#181c27", bd=0)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=380)

        tk.Label(frame, text="🏪", font=("Segoe UI Emoji", 36),
                 bg="#181c27", fg="#f59e0b").pack(pady=(30, 4))
        tk.Label(frame, text="KhataSystem", font=("Georgia", 20, "bold"),
                 bg="#181c27", fg="#f59e0b").pack()
        tk.Label(frame, text="Shop Credit Ledger", font=("Courier", 9),
                 bg="#181c27", fg="#64748b").pack(pady=(2, 24))

        for label, attr, show in [("Username", "username_var", ""), ("Password", "password_var", "*")]:
            tk.Label(frame, text=label, font=("Courier", 9),
                     bg="#181c27", fg="#64748b").pack(anchor="w", padx=30)
            var = tk.StringVar()
            setattr(self, attr, var)
            e = tk.Entry(frame, textvariable=var, show=show,
                         font=("Courier", 11), bg="#1e2435", fg="#e2e8f0",
                         insertbackground="#f59e0b", relief="flat", bd=0)
            e.pack(fill="x", padx=30, ipady=8, pady=(2, 12))

        self.username_var.set("admin")
        self.err_label = tk.Label(frame, text="", font=("Courier", 9),
                                  bg="#181c27", fg="#ef4444")
        self.err_label.pack()

        btn = tk.Button(frame, text="Login →", font=("Courier", 11, "bold"),
                        bg="#f59e0b", fg="#000", relief="flat", bd=0,
                        activebackground="#b45309", cursor="hand2",
                        command=self._login)
        btn.pack(fill="x", padx=30, ipady=9, pady=(6, 0))
        self.root.bind("<Return>", lambda e: self._login())

    def _login(self):
        u = self.username_var.get().strip()
        p = self.password_var.get().strip()
        user = db.verify_login(u, p)
        if user:
            self.root.destroy()
            self.on_success(user)
        else:
            self.err_label.config(text="Invalid username or password.")
