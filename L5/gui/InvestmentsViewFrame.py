import tkinter as tk


import utils.main_utility as utility


class InvestmentsViewFrame(tk.Toplevel):
    BACKGROUND_COLOUR = '#6b7272'
    TEXT_COLOUR = 'white'
    FONT = 'Calibri'

    def __init__(self, parent):
        super().__init__(parent, bg=self.BACKGROUND_COLOUR)
        icon = tk.PhotoImage(file='img\dollar.png')
        self.iconphoto(False, icon)
        self.minsize(500, 400)

        self.__data_from_json = utility.load_portfolio()
        self.__api_categories = ["currency", "foreign_stock", "crypto_currency", "polish_stock"]
        self.__api_categories_headers = ["Waluty", "Akcje zagraniczne", "Krypto waluty", "Akcje polskie"]
        self.__base_currency = self.__data_from_json["base_currency"]

        i = 0
        for name in self.__api_categories:
            self.__category_label = tk.Label(self, text=self.__api_categories_headers[i], bg=self.BACKGROUND_COLOUR,
                                             fg=self.TEXT_COLOUR, font=(self.FONT, 20))
            self.__category_label.pack(pady=2, anchor='w', padx=(10, 0))
            for invest in self.__data_from_json[name]:
                self.__inv_label = tk.Label(self, text=f'Symbol: {invest["symbol"]},  śr. cena zakupu: '
                                                       f'{invest["avg_price"]} {self.__base_currency},'
                                                       f'  ilość: {invest["quantity"]}', bg=self.BACKGROUND_COLOUR,
                                            fg=self.TEXT_COLOUR, font=(self.FONT, 13))
                self.__inv_label.pack(pady=2, anchor='w', padx=(20, 0))
            i += 1
