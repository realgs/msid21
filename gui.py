import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkinter.constants import NSEW

ICON = 'favicon.ico'


def read_from_file(path):
    try:
        file = open(path, mode="r", encoding='utf-8')
    except OSError:
        tk.messagebox.showerror('Error', 'Nie znaleziono pliku')
        return 1
    lines_tmp = file.readlines()
    file.close()
    return lines_tmp


class Gui(tk.Frame):
    def __init__(self, master=tk.Tk()):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.parent.title('Investment Portfolio')
        self.parent.iconbitmap(ICON)
        self.parent.geometry('1400x800')
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self.parent.resizable(False, False)
        self.parent.columnconfigure(0, weight=999)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=9999)
        self.parent.rowconfigure(2, weight=1)
        self.working_frame = tk.Frame(self.parent, background='#00704A')
        self.wallet = tk.Label(self.working_frame)
        self.resource_type_label = tk.Label(self.wallet, text='Typ zasobu: ')
        self.resource_type = ttk.Combobox(self.wallet, width=15, state='readonly')
        self.resource_label = tk.Label(self.wallet, text='Nazwa zasobu: ')
        self.resource = tk.Entry(self.wallet, width=15)
        self.quantity_label = tk.Label(self.wallet, text='Ilość zasobu: ')
        self.quantity = tk.Entry(self.wallet, width=15)
        self.price_label = tk.Label(self.wallet, text='Cena zasobu: ')
        self.price = tk.Entry(self.wallet, width=15)
        self.currency = ttk.Combobox(self.wallet, width=5, state='readonly')
        self.button_add = tk.Button(self.wallet, padx=30, pady=5, text='Dodaj do portfela')
        self.investments = tk.Label(self.working_frame)
        self.text = tk.Text(self.investments, height=100, width=145)
        self.scrollbar = ttk.Scrollbar(self.investments, command=self.text.yview)
        self.options = tk.Label(self.working_frame)
        self.percent_label = tk.Label(self.options, text='Procent zasobów do sprzedaży:')
        self.percent = tk.Entry(self.options, width=15, justify='right')
        self.button_update = tk.Button(self.options, padx=55, pady=5, text='Odśwież portfolio')
        self.button_show_portfolio = tk.Button(self.options, padx=67, pady=5, text='Pokaż portfolio')
        self.button_show_wallet = tk.Button(self.options, padx=67, pady=5, text='Pokaż portfel')
        self.create_working_space()

    def create_working_space(self):
        self.working_frame.grid(row=1, column=0, columnspan=1, rowspan=1, sticky=NSEW)
        self.wallet.pack(side='top', fill='x')
        self.resource_type_label.grid(row=0, column=0, padx=3)
        self.resource_type.grid(row=0, column=1)
        self.resource_label.grid(row=0, column=2, padx=3)
        self.resource.grid(row=0, column=3)
        self.quantity_label.grid(row=0, column=4, padx=3)
        self.quantity.grid(row=0, column=5)
        self.price_label.grid(row=0, column=6, padx=3)
        self.price.grid(row=0, column=7)
        self.currency.grid(row=0, column=8)
        self.button_add.grid(row=0, column=9, padx=10)

        self.investments.rowconfigure(0, weight=1)
        self.investments.columnconfigure(0, weight=1)
        self.investments.pack(side='right', fill='both')
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set

        self.options.rowconfigure(5, weight=1)
        self.options.columnconfigure(1, weight=1)
        self.options.pack(side='left', fill='both')
        self.percent_label.grid(row=0, column=0, pady=3)
        self.percent.grid(row=1, column=0, pady=5)
        self.button_update.grid(row=2, column=0, pady=10)
        self.button_show_portfolio.grid(row=3, column=0, pady=10)
        self.button_show_wallet.grid(row=4, column=0, pady=10)

    def quit(self):
        self.parent.destroy()

    @staticmethod
    def set_combobox_values(box, values, current):
        box['values'] = values
        box.current(current)

    @staticmethod
    def set_button_command(button, command):
        button.config(command=command)

    @staticmethod
    def set_label_txt(label, message):
        label.config(text=message)

    @staticmethod
    def set_entry_value(entry, value):
        entry.insert(0, value)

    @staticmethod
    def throw_error(title, message):
        tk.messagebox.showerror(title, message)


if __name__ == '__main__':
    gui = Gui()
    gui.mainloop()
