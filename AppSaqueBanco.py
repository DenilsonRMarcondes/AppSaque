# python
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

def create_account(owner: str, initial: float = 0.0):
    balance = float(initial)

    def deposit(amount: float):
        nonlocal balance
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Valor de depósito deve ser positivo")
        balance += amount
        return balance

    def withdraw(amount: float):
        nonlocal balance
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Valor do PIX deve ser positivo")
        if amount > balance:
            raise ValueError("Saldo insuficiente")
        balance -= amount
        return balance

    def get_balance():
        return balance

    def transfer(target_account, amount: float):
        if not isinstance(target_account, dict) or 'deposit' not in target_account:
            raise TypeError("Conta de destino inválida")
        withdraw(amount)
        target_account['deposit'](amount)
        return balance

    return {
        'owner': owner,
        'deposit': deposit,
        'withdraw': withdraw,
        'get_balance': get_balance,
        'transfer': transfer
    }

class AccountGUI:
    def __init__(self, root: tk.Tk, account: dict):
        self.root = root
        self.account = account
        self.root.title("Conta — Painel Executivo")
        self.root.geometry("420x220")
        self.root.resizable(False, False)
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style(self.root)
        # Usa tema nativo e configura cores sóbrias
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background='#F4F6F7')
        style.configure('Card.TFrame', background='#FFFFFF', relief='flat')
        style.configure('Title.TLabel', background='#F4F6F7', foreground='#2C3E50',
                        font=('Segoe UI', 12, 'bold'))
        style.configure('Balance.TLabel', background='#FFFFFF', foreground='#2C3E50',
                        font=('Segoe UI', 20))
        style.configure('TLabel', background='#F4F6F7', foreground='#2C3E50', font=('Segoe UI', 10))
        style.configure('TEntry', padding=6, relief='flat', font=('Segoe UI', 10))
        style.configure('Accent.TButton', background='#2F4F4F', foreground='#FFFFFF',
                        font=('Segoe UI', 10, 'bold'), padding=6)
        style.map('Accent.TButton',
                  background=[('active', '#2F4F4F'), ('!disabled', '#2F4F4F')])

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12, style='TFrame')
        container.pack(fill='both', expand=True)

        card = ttk.Frame(container, padding=(16, 12), style='Card.TFrame')
        card.place(relx=0.5, rely=0.5, anchor='center', width=380, height=160)

        # Título e proprietário
        title = ttk.Label(card, text=f"Conta — {self.account['owner']}", style='Title.TLabel')
        title.pack(anchor='w')

        # Saldo
        self.balance_var = tk.StringVar(value=f"R$ {self.account['get_balance']():.2f}")
        balance_label = ttk.Label(card, textvariable=self.balance_var, style='Balance.TLabel')
        balance_label.pack(anchor='w', pady=(6, 12))

        # Linha de saque
        row = ttk.Frame(card, style='Card.TFrame')
        row.pack(fill='x')
        amt_label = ttk.Label(row, text="Enviar PIX:", width=16)
        amt_label.pack(side='left')

        vcmd = (self.root.register(self._validate_amount), '%P')
        self.amount_entry = ttk.Entry(row, validate='key', validatecommand=vcmd, width=18)
        self.amount_entry.pack(side='left', padx=(6, 8))
        self.amount_entry.insert(0, "0.00")

        withdraw_btn = ttk.Button(row, text="Sacar", style='Accent.TButton', command=self._on_withdraw)
        withdraw_btn.pack(side='left')

        # Mensagem discreta
        hint = ttk.Label(card, text="Operação segura — valores em reais (use ponto para decimais).", font=('Segoe UI', 8))
        hint.pack(anchor='w', pady=(8, 0))

        # Enter para sacar
        self.root.bind('<Return>', lambda e: self._on_withdraw())

    def _validate_amount(self, proposed: str) -> bool:
        if proposed == "":
            return True
        try:
            # aceita apenas números e ponto
            val = float(proposed)
            return val >= 0
        except Exception:
            return False

    def _on_withdraw(self):
        raw = self.amount_entry.get().strip()
        try:
            amount = float(raw)
        except Exception:
            messagebox.showerror("Entrada inválida", "Digite um número válido para o valor.")
            return

        try:
            new_balance = self.account['withdraw'](amount)
        except ValueError as e:
            messagebox.showwarning("Operação cancelada", str(e))
            return
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {type(e).__name__} {e}")
            return

        self.balance_var.set(f"R$ {new_balance:.2f}")
        # feedback sutil
        messagebox.showinfo("PIX efetuado", f"PIX de R$ {amount:.2f} realizado com sucesso.")

def main():
    acc = create_account("Denilson", 1000.00)
    root = tk.Tk()
    app = AccountGUI(root, acc)
    root.mainloop()

if __name__ == '__main__':
    main()
