import tkinter as tk
from tkinter import messagebox as msb

import gui.InvestmentsViewFrame as InvestmentsViewFrame
import gui.AddInvestmentFrame as AddInvestmentFrame
import gui.DeleteInvestWindow as DeleteInvestWindow


class MainFrame(tk.Frame):
    BACKGROUND_COLOUR = '#6b7272'
    TEXT_COLOUR = 'white'
    FONT = 'Calibri'

    def __init__(self, master=None):
        # init self
        tk.Frame.__init__(self, master, bg=self.BACKGROUND_COLOUR)
        self.pack()

        # frames for components
        # components are initialized in init methods
        self.__logo_frame = tk.Frame(self, bg=self.BACKGROUND_COLOUR)
        self.__logo_frame.pack()
        self.__buttons_frame = tk.Frame(self, bg=self.BACKGROUND_COLOUR)
        self.__buttons_frame.pack()

        # init components in their frames
        self.__init_logo()
        self.__init_buttons()

    def __init_logo(self):
        self.__logo = tk.Label(self.__logo_frame, text="Portfolio inwestycyjne", bg=self.BACKGROUND_COLOUR,
                               fg=self.TEXT_COLOUR, font=(self.FONT, 38))
        self.__logo.pack(pady=(50, 10))

    def __init_buttons(self):
        self.__add_invest_button = tk.Button(self.__buttons_frame, text="Dodaj zasób do portfela", font=(self.FONT, 11),
                                             command=lambda: self.__add_invest_button_clicked(), width=25)
        self.__add_invest_button.grid(row=0, column=0, pady=(5, 5))

        self.__show_invest_button = tk.Button(self.__buttons_frame, text="Pokaż zasoby portfela", font=(self.FONT, 11),
                                              command=lambda: self.__show_invest_button_clicked(), width=25)
        self.__show_invest_button.grid(row=1, column=0, pady=(5, 5))

        self.__delete_invest_button = tk.Button(self.__buttons_frame, text="Usuń zasób z portfela",
                                                font=(self.FONT, 11),
                                                command=lambda: self.__delete_invest_button_clicked(), width=25)
        self.__delete_invest_button.grid(row=2, column=0, pady=(5, 5))

        self.__close_button = tk.Button(self.__buttons_frame, text="Zakończ ustawianie portfela", font=(self.FONT, 11),
                                        command=lambda: self.master.destroy(), width=25)
        self.__close_button.grid(row=3, column=0, pady=(5, 10))

    def __add_invest_button_clicked(self):
        i = AddInvestmentFrame.AddInvestmentFrame(self)

    def __show_invest_button_clicked(self):
        i = InvestmentsViewFrame.InvestmentsViewFrame(self)

    def __delete_invest_button_clicked(self):
        i = DeleteInvestWindow.DeleteInvestWindow(self)
