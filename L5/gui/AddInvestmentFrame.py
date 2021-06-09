import tkinter as tk
from tkinter import messagebox as msb


import utils.main_utility as utility


class AddInvestmentFrame(tk.Toplevel):
    BACKGROUND_COLOUR = '#6b7272'
    TEXT_COLOUR = 'white'
    FONT = 'Calibri'

    def __init__(self, parent):
        # init self
        super().__init__(parent, bg=self.BACKGROUND_COLOUR)
        icon = tk.PhotoImage(file='img\dollar.png')
        self.iconphoto(False, icon)
        self.minsize(800, 270)

        self.__name = tk.StringVar()
        self.__quantity = tk.StringVar()
        self.__cost = tk.StringVar()
        self.__type = tk.StringVar()
        self.__type.set("Ivalid")
        self.__api = tk.StringVar()
        self.__api.set("Ivalid")
        self.__types = {"Waluty": 'currency', "Akcje zagraniczne": 'foreign_stock', "Krypto waluty": 'crypto_currency',
                        "Akcje polskie": 'polish_stock'}
        self.__apis = {"BitBay": "BitBay", "Bittrex": "Bittrex"}

        self.__data_from_json = utility.load_portfolio()

        self.__name_label = tk.Label(self, text="Podaj nazwę zasobu", bg=self.BACKGROUND_COLOUR,
                                     fg=self.TEXT_COLOUR, font=(self.FONT, 13))
        self.__name_label.grid(row=0, column=0, sticky='w', pady=(15, 5), padx=(10, 0))

        self.__entry_name = tk.Entry(self, textvariable=self.__name, width=55, font=(self.FONT, 13))
        self.__entry_name.grid(row=0, column=1, padx=5, pady=(15, 5), sticky='w')

        self.__quantity_label = tk.Label(self, text="Podaj ilość zasobu", bg=self.BACKGROUND_COLOUR,
                                         fg=self.TEXT_COLOUR, font=(self.FONT, 13))
        self.__quantity_label.grid(row=1, column=0, sticky='w', pady=5, padx=(10, 0))

        self.__entry_quantity = tk.Entry(self, textvariable=self.__quantity, width=55, font=(self.FONT, 13))
        self.__entry_quantity.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.__cost_label = tk.Label(self, text="Podaj średnią cenę zakupu", bg=self.BACKGROUND_COLOUR,
                                     fg=self.TEXT_COLOUR, font=(self.FONT, 13))
        self.__cost_label.grid(row=2, column=0, sticky='w', pady=5, padx=(10, 0))

        self.__entry_cost = tk.Entry(self, textvariable=self.__cost, width=55, font=(self.FONT, 13))
        self.__entry_cost.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        self.__type_label = tk.Label(self, text="Wybierz typ", bg=self.BACKGROUND_COLOUR,
                                     fg=self.TEXT_COLOUR, font=(self.FONT, 13))
        self.__type_label.grid(row=3, column=0, sticky='w', pady=5, padx=(10, 0))

        self.__type_frame = tk.Frame(self)
        self.__type_frame.grid(row=3, column=1, sticky='w')

        i = 0
        for (text, value) in self.__types.items():
            self.__type_radio = tk.Radiobutton(self.__type_frame, text=text, variable=self.__type, value=value,
                                               bg=self.BACKGROUND_COLOUR, fg='black', font=(self.FONT, 13),
                                               activebackground=self.BACKGROUND_COLOUR)
            self.__type_radio.grid(row=0, column=i)
            i += 1

        self.__apis_label = tk.Label(self, text="Wybierz giełdę (tylko dla kryptowalut)", bg=self.BACKGROUND_COLOUR,
                                     fg=self.TEXT_COLOUR, font=(self.FONT, 13))
        self.__apis_label.grid(row=4, column=0, sticky='w', pady=5, padx=(10, 0))

        self.__apis_frame = tk.Frame(self)
        self.__apis_frame.grid(row=4, column=1, sticky='w')

        i = 0
        for (text, value) in self.__apis.items():
            self.__apis_radio = tk.Radiobutton(self.__apis_frame, text=text, variable=self.__api, value=value,
                                               bg=self.BACKGROUND_COLOUR, fg='black', font=(self.FONT, 13),
                                               activebackground=self.BACKGROUND_COLOUR)
            self.__apis_radio.grid(row=0, column=i)
            i += 1

        self.__add_button = tk.Button(self, text="Dodaj", font=(self.FONT, 11),
                                      command=lambda: self.__add_to_portfolio(), width=20)
        self.__add_button.grid(row=5, column=0, columnspan=2, pady=(20, 5))

    def __add_to_portfolio(self):
        try:
            price = float(self.__cost.get())
            quan = float(self.__quantity.get())
            if self.__name.get() == "":
                raise ValueError
            if self.__type.get() == "Ivalid":
                raise ValueError

            if self.__name.get() == "crypto_currency":
                if self.__api.get() == "Ivalid":
                    raise ValueError
                self.__data_from_json[self.__type.get()].append({"symbol": self.__name.get(),
                                                                 "avg_price": price, "quantity": quan,
                                                                 "api": str(self.__api.get())})

            else:
                self.__data_from_json[self.__type.get()].append({"symbol": self.__name.get(),
                                                                 "avg_price": price, "quantity": quan})
            utility.save_portfolio(self.__data_from_json)
            msb.showinfo('INFO', 'Saved successfully')
            self.destroy()
        except ValueError:
            msb.showerror('ERROR', 'You gave wrong values. Did not save any changes')
            self.destroy()
