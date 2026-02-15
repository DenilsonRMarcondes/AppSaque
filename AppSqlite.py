# =========================
# Banco com SQLite + Tkinter
# =========================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

#Esse app conta com conexao com banco de dados SQLite para armazenar o saldo da conta e foi desenvolvido com ajuda da inteligência artificial

#teste de commit na branch de dev para testar ver se o github está configurado
# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

DB_NAME = "bank.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL UNIQUE,
                balance REAL NOT NULL
            )
        """)
        conn.commit()


# =========================
# MODELO DA CONTA (NEGÓCIO)
# =========================

class Account:
    def __init__(self, owner: str, initial: float = 0.0):
        self.owner = owner
        self._ensure_account(initial)

    def _ensure_account(self, initial):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM accounts WHERE owner = ?",
                (self.owner,)
            )
            result = cursor.fetchone()

            if result is None:
                cursor.execute(
                    "INSERT INTO accounts (owner, balance) VALUES (?, ?)",
                    (self.owner, initial)
                )
                conn.commit()

    def get_balance(self) -> float:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT balance FROM accounts WHERE owner = ?",
                (self.owner,)
            )
            return cursor.fetchone()[0]

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("O valor do saque deve ser positivo.")

        balance = self.get_balance()
        if amount > balance:
            raise ValueError("Saldo insuficiente.")

        new_balance = balance - amount

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET balance = ? WHERE owner = ?",
                (new_balance, self.owner)
            )
            conn.commit()

        return new_balance


# =========================
# INTERFACE GRÁFICA (GUI)
# =========================

class AccountGUI:
    def __init__(self, root: tk.Tk, account: Account):
        self.root = root
        self.account = account

        self.root.title("Conta Bancária — SQLite")
        self.root.geometry("420x220")
        self.root.resizable(False, False)

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TFrame', background='#F4F6F7')
        style.configure('Card.TFrame', background='#FFFFFF')
        style.configure('Title.TLabel',
                        font=('Segoe UI', 12, 'bold'),
                        foreground='#2C3E50',
                        background='#FFFFFF')
        style.configure('Balance.TLabel',
                        font=('Segoe UI', 20),
                        foreground='#2C3E50',
                        background='#FFFFFF')
        style.configure('Accent.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        padding=6)

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill='both', expand=True)

        card = ttk.Frame(container, padding=16, style='Card.TFrame')
        card.place(relx=0.5, rely=0.5, anchor='center', width=380, height=160)

        # Título
        ttk.Label(
            card,
            text=f"Conta — {self.account.owner}",
            style='Title.TLabel'
        ).pack(anchor='w')

        # Saldo
        self.balance_var = tk.StringVar()
        self._update_balance()

        ttk.Label(
            card,
            textvariable=self.balance_var,
            style='Balance.TLabel'
        ).pack(anchor='w', pady=(6, 12))

        # Linha de saque
        row = ttk.Frame(card)
        row.pack(fill='x')

        ttk.Label(row, text="Valor para sacar:", width=16).pack(side='left')

        self.amount_entry = ttk.Entry(row, width=18)
        self.amount_entry.pack(side='left', padx=(6, 8))
        self.amount_entry.insert(0, "0.00")

        ttk.Button(
            row,
            text="Sacar",
            style='Accent.TButton',
            command=self._on_withdraw
        ).pack(side='left')

        # Enter executa o saque
        self.root.bind('<Return>', lambda e: self._on_withdraw())

    def _update_balance(self):
        balance = self.account.get_balance()
        self.balance_var.set(f"R$ {balance:.2f}")

    def _on_withdraw(self):
        try:
            amount = float(self.amount_entry.get())
            new_balance = self.account.withdraw(amount)
            self._update_balance()
            messagebox.showinfo(
                "Saque realizado",
                f"Saque de R$ {amount:.2f} efetuado com sucesso."
            )
        except ValueError as e:
            messagebox.showwarning("Operação inválida", str(e))
        except Exception as e:
            messagebox.showerror("Erro inesperado", str(e))


# =========================
# PROGRAMA PRINCIPAL
# =========================

def main():
    setup_database()

    account = Account("Novo User", 1000.00)

    root = tk.Tk()
    app = AccountGUI(root, account)
    root.mainloop()


if __name__ == "__main__":
    main()
