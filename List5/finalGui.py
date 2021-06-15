import tkinter as tk
from tkinter import ttk, NSEW
from StockData.dataKeys import ASSET_TYPES
import tkinter.messagebox

HEIGHT = 700
WIDTH = 1400


def set_button_command(button, command):
    button.config(command=command)


def show_error(title, message):
    tk.messagebox.showerror(title, message)


class Gui(tk.Frame):
    def __init__(self, master=tk.Tk()):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.parent.title('Project: Investment Portfolio')
        self.parent.geometry('1500x700')
        self.parent.resizable(True, True)
        self.parent.protocol(self.close)

        self.working_frame = tk.Frame(self.parent)
        self.working_frame.grid(row=0, column=0, columnspan=1, rowspan=1, sticky=NSEW)

        self.data = tk.Label(self.working_frame, background='#FAF0E6')
        self.data.pack(side='left', fill='both')

        self.asset_label = tk.Label(self.data, text='Asset shortcut name: ', bg='#FAF0E6')
        self.asset_label.config(font=("Arial", 10))
        self.asset_label.grid(row=0, column=0, padx=5, pady=5)
        self.asset = tk.Entry(self.data, width=20, justify='center')
        self.asset.grid(row=1, column=0)

        self.asset_type_label = tk.Label(self.data, text='Asset type: ', bg='#FAF0E6')
        self.asset_type_label.config(font=("Arial", 10))
        self.asset_type_label.grid(row=2, column=0, padx=5, pady=5)
        self.asset_type = ttk.Combobox(self.data, width=17, justify='center', state='readonly')
        self.asset_type['values'] = ASSET_TYPES
        self.asset_type.grid(row=3, column=0)
        self.asset_type.current()

        self.volume_label = tk.Label(self.data, text='Asset volume: ', bg='#FAF0E6')
        self.volume_label.config(font=("Arial", 10))
        self.volume_label.grid(row=4, column=0, padx=5, pady=5)
        self.volume = tk.Entry(self.data, width=20, justify='center')
        self.volume.grid(row=5, column=0)

        self.price_label = tk.Label(self.data, text='Asset average price: ', bg='#FAF0E6')
        self.price_label.config(font=("Arial", 10))
        self.price_label.grid(row=6, column=0, padx=5, pady=5)
        self.price = tk.Entry(self.data, width=20, justify='center')
        self.price.grid(row=7, column=0)

        self.currency_label = tk.Label(self.data, text='Purchase currency:', bg='#FAF0E6')
        self.currency_label.config(font=("Arial", 10))
        self.currency_label.grid(row=8, column=0, padx=5, pady=5)
        self.currency = ttk.Combobox(self.data, width=17, justify='center', state='readonly')
        self.currency['values'] = ('PLN', 'USD', 'EUR')
        self.currency.grid(row=9, column=0)
        self.currency.current()

        self.button_add = tk.Button(self.data, text='Add new asset', height=2, width=20, bg='#DEB887')
        self.button_add.grid(row=10, column=0, padx=5, pady=10)

        self.button_show_wallet = tk.Button(self.data, text='Show wallet', height=2, width=20, bg='#DEB887')
        self.button_show_wallet.grid(row=12, column=0, padx=5, pady=10)

        self.percent_label = tk.Label(self.data, text='Percent of value:', bg='#FAF0E6')
        self.percent_label.config(font=("Arial", 10))
        self.percent_label.grid(row=13, column=0, padx=5, pady=5)
        self.percent = tk.Entry(self.data, width=15, justify='center')
        self.percent.grid(row=14, column=0, padx=5, pady=5)
        self.percent.insert(0, '10')

        self.button_show_portfolio = tk.Button(self.data, text='Show portfolio', height=2, width=20, bg='#DEB887')
        self.button_show_portfolio.grid(row=16, column=0, padx=5, pady=10)

        self.screen = tk.Label(self.working_frame)
        self.screen.pack(side='right', fill='both')
        self.text = tk.Text(self.screen, height=100, width=160)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self.screen, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set

    def close(self):
        self.destroy()


#if __name__ == '__main__':
  #  gui = Gui()
  #  gui.mainloop()
