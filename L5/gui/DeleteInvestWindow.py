import tkinter as tk
from tkinter import messagebox as msb


import utils.main_utility as utility


class DeleteInvestWindow(tk.Toplevel):
    BACKGROUND_COLOUR = '#6b7272'
    TEXT_COLOUR = 'white'
    FONT = 'Calibri'

    def __init__(self, parent):
        # init self
        super().__init__(parent, bg=self.BACKGROUND_COLOUR)
        icon = tk.PhotoImage(file='img\dollar.png')
        self.iconphoto(False, icon)
        self.minsize(500, 340)

        # init values etc.
        self.__data_from_json = utility.load_portfolio()
        self.__api_names = ["currency", "foreign_stock", "crypto_currency", "polish_stock"]
        self.__chosen_symbol = tk.IntVar()

        # frames for components
        # components are initialized in init methods
        self.__main_label_frame = tk.Frame(self, bg=self.BACKGROUND_COLOUR)
        self.__main_label_frame.pack(anchor='w', padx=(10, 0))
        self.__radiobuttons_frame = tk.Frame(self, bg=self.BACKGROUND_COLOUR)
        self.__radiobuttons_frame.pack()

        # init components in their frames
        self.__init_main_label()
        self.__init_radiobuttons()
        self.__init_accept_button()

    def __init_main_label(self):
        self.__main_label = tk.Label(self.__main_label_frame, text="Wybierz co chcesz usunąć",
                                     bg=self.BACKGROUND_COLOUR, fg=self.TEXT_COLOUR, font=(self.FONT, 20), anchor='w')
        self.__main_label.pack(pady=10, anchor='w')

    def __init_radiobuttons(self):
        i = 0
        for name in self.__api_names:
            for invest in self.__data_from_json[name]:
                r_button = tk.Radiobutton(self.__radiobuttons_frame,
                                          text=f'Symbol: {invest["symbol"]}, avg. price: {invest["avg_price"]} '
                                               f'{self.__data_from_json["base_currency"]}, quantity: '
                                               f'{invest["quantity"]}',
                                          variable=self.__chosen_symbol, value=i, bg=self.BACKGROUND_COLOUR,
                                          fg='black', font=(self.FONT, 13), activebackground=self.BACKGROUND_COLOUR)
                r_button.grid(row=i, column=0, sticky='w', padx=(10, 0))
                i += 1

    def __init_accept_button(self):
        self.__add_button = tk.Button(self, text="Usuń", font=(self.FONT, 11),
                                      command=lambda: self.__delete_from_portfolio())
        self.__add_button.pack(pady=(25, 5))

    def __delete_from_portfolio(self):
        counter = 0
        for name in self.__api_names:
            k = 0
            for invest in self.__data_from_json[name]:
                if counter == self.__chosen_symbol.get():
                    self.__data_from_json[name].pop(k)
                    utility.save_portfolio(self.__data_from_json)
                    msb.showinfo('INFO', 'Deleted successfully')
                    self.destroy()
                    return
                k += 1
                counter += 1
