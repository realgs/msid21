import tkinter as tk
from tkinter import ttk, NSEW
from StockData.dataKeys import ASSET_TYPES
import tkinter.messagebox

HEIGHT = 700
WIDTH = 1400


def configButtonCommand(button, command):
    button.config(command=command)


def throwError(title, message):
    tk.messagebox.showerror(title, message)


class Gui(tk.Frame):
    def __init__(self, master=tk.Tk()):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.parent.title('Project: Investment Portfolio')
        self.parent.geometry('1500x700')
        self.parent.resizable(True, True)
        self.parent.protocol(self.close)

        self.frame = tk.Frame(self.parent)
        self.frame.grid(row=0, column=0, columnspan=1, rowspan=1, sticky=NSEW)

        self.data = tk.Label(self.frame, background='#FAF0E6')
        self.data.pack(side='left', fill='both')

        self.assetLabel = tk.Label(self.data, text='Asset shortcut name: ', bg='#FAF0E6')
        self.assetLabel.config(font=("Arial", 10))
        self.assetLabel.grid(row=0, column=0, padx=5, pady=5)
        self.asset = tk.Entry(self.data, width=20, justify='center')
        self.asset.grid(row=1, column=0)

        self.assetTypeLabel = tk.Label(self.data, text='Asset type: ', bg='#FAF0E6')
        self.assetTypeLabel.config(font=("Arial", 10))
        self.assetTypeLabel.grid(row=2, column=0, padx=5, pady=5)
        self.assetType = ttk.Combobox(self.data, width=17, justify='center', state='readonly')
        self.assetType['values'] = ASSET_TYPES
        self.assetType.grid(row=3, column=0)
        self.assetType.current()

        self.volumeLabel = tk.Label(self.data, text='Asset volume: ', bg='#FAF0E6')
        self.volumeLabel.config(font=("Arial", 10))
        self.volumeLabel.grid(row=4, column=0, padx=5, pady=5)
        self.volume = tk.Entry(self.data, width=20, justify='center')
        self.volume.grid(row=5, column=0)

        self.priceLabel = tk.Label(self.data, text='Asset average price: ', bg='#FAF0E6')
        self.priceLabel.config(font=("Arial", 10))
        self.priceLabel.grid(row=6, column=0, padx=5, pady=5)
        self.price = tk.Entry(self.data, width=20, justify='center')
        self.price.grid(row=7, column=0)

        self.currencyLabel = tk.Label(self.data, text='Purchase currency:', bg='#FAF0E6')
        self.currencyLabel.config(font=("Arial", 10))
        self.currencyLabel.grid(row=8, column=0, padx=5, pady=5)
        self.currency = ttk.Combobox(self.data, width=17, justify='center', state='readonly')
        self.currency['values'] = ('PLN', 'USD', 'EUR')
        self.currency.grid(row=9, column=0)
        self.currency.current()

        self.buttonAdd = tk.Button(self.data, text='Add new asset', height=2, width=20, bg='#DEB887')
        self.buttonAdd.grid(row=10, column=0, padx=5, pady=10)

        self.buttonShowWallet = tk.Button(self.data, text='Show wallet', height=2, width=20, bg='#DEB887')
        self.buttonShowWallet.grid(row=12, column=0, padx=5, pady=10)

        self.percentLabel = tk.Label(self.data, text='Percent of value:', bg='#FAF0E6')
        self.percentLabel.config(font=("Arial", 10))
        self.percentLabel.grid(row=13, column=0, padx=5, pady=5)
        self.percent = tk.Entry(self.data, width=15, justify='center')
        self.percent.grid(row=14, column=0, padx=5, pady=5)
        self.percent.insert(0, '10')

        self.buttonShowPortfolio = tk.Button(self.data, text='Show portfolio', height=2, width=20, bg='#DEB887')
        self.buttonShowPortfolio.grid(row=16, column=0, padx=5, pady=10)

        self.buttonClear = tk.Button(self.data, text='Clear', height=2, width=20, bg='#DEB887')
        self.buttonClear.grid(row=17, column=0, padx=5, pady=10)
        self.buttonClear.config(command=self.clearScreen)

        self.screen = tk.Label(self.frame)
        self.screen.pack(side='right', fill='both')
        self.text = tk.Text(self.screen, height=100, width=160)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self.screen, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set

    def close(self):
        self.destroy()

    def clearScreen(self):
        self.text.delete(1.0, 'end')
