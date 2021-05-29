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
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.parent.title('Investment Portfolio')
        self.parent.iconbitmap(ICON)
        self.parent.geometry('1150x800')
        self.parent.columnconfigure(0, weight=999)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=9999)
        self.parent.rowconfigure(2, weight=1)
        self.working_frame = tk.Frame(self.parent, background='#00704A')
        self.wallet = tk.Label(self.working_frame)
        self.resource_type_label = tk.Label(self.wallet, text='Resource type: ')
        self.resource_type = ttk.Combobox(self.wallet, width=10, state='readonly')
        self.resource_label = tk.Label(self.wallet, text='Resource name: ')
        self.resource = tk.Entry(self.wallet, width=15)
        self.quantity_label = tk.Label(self.wallet, text='Resource quantity: ')
        self.quantity = tk.Entry(self.wallet, width=15)
        self.price_label = tk.Label(self.wallet, text='Resource price: ')
        self.price = tk.Entry(self.wallet, width=15)
        self.currency = ttk.Combobox(self.wallet, width=10, state='readonly')
        self.button_add = tk.Button(self.wallet, padx=70, pady=5, text='Add to wallet')
        self.investments = tk.Label(self.working_frame)
        self.text = tk.Text(self.investments, height=100, width=93, state='disabled')
        self.scrollbar = ttk.Scrollbar(self.investments, command=self.text.yview)
        self.create_working_space()

    def create_working_space(self):
        self.working_frame.grid(row=1, column=0, columnspan=1, rowspan=1, sticky=NSEW)
        self.wallet.pack(side='top', fill='x')
        self.resource_type_label.grid(row=0, column=0)
        self.resource_type.grid(row=0, column=1)
        self.resource_label.grid(row=0, column=2)
        self.resource.grid(row=0, column=3)
        self.quantity_label.grid(row=0, column=4)
        self.quantity.grid(row=0, column=5)
        self.price_label.grid(row=0, column=6)
        self.price.grid(row=0, column=7)
        self.currency.grid(row=0, column=8)
        self.button_add.grid(row=0, column=9)

        self.investments.rowconfigure(0, weight=1)
        self.investments.columnconfigure(0, weight=1)
        self.investments.pack(side='bottom', fill='both')
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set

    @staticmethod
    def set_combobox_values(box, values, current):
        box['values'] = values
        box.current(current)


if __name__ == '__main__':
    gui = Gui(tk.Tk())
    gui.mainloop()
