from stock_exchange.GUI.asset_form import *
from stock_exchange.GUI.assets_list import AssetsList
from tkinter import messagebox
import json


class WalletGUI(Tk):
    def __init__(self, base_currency):
        super().__init__()
        self._assets = []
        self._base_currency = base_currency
        self._configure_root()
        self._add_buttons()
        self.mainloop()

    def _configure_root(self):
        self.title("Wallet")
        self.geometry("530x160+900+500")
        self.configure(bg="#2a9d8f")
        self.iconbitmap("../Images/icon.ico")
        self.resizable(False, False)

    def _add_buttons(self):
        Button(self, text="Add new asset", width=self.winfo_width(), bg="#2F3D3B", fg="#ECFDFA", font=('Bahnschrift Light', 16),
               command=lambda: self._asset_form()).pack(padx=5, pady=5)
        Button(self, text="Display owned assets", width=self.winfo_width(), bg='#2F3D3B', fg="#ECFDFA", font=('Bahnschrift Light', 16),
               command=lambda: self._display_asset_summary()).pack(padx=5, pady=5)
        Button(self, text="Export to json", width=self.winfo_width(), bg='#2F3D3B', fg='#ECFDFA', font=('Bahnschrift Light', 16),
               command=lambda: self._export_to_json()).pack(padx=5, pady=5)

    @property
    def assets(self):
        return self._assets

    @property
    def base_currency(self):
        return self._base_currency

    def _display_asset_summary(self):
        AssetsList(root=self)

    def _asset_form(self):
        AssetForm(root=self)

    def _export_to_json(self):
        with open('../Resources/wallet.json', 'w') as json_file:
            data_set = {"base_currency": self._base_currency, "assets": self._assets}
            json.dump(data_set, json_file)
            messagebox.showinfo("Wallet", message="Wallet successfully exported!")
