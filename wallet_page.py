from tkinter import *
from tkinter import ttk
import tkinter
import constants
import gui


class WalletPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background=constants.BACKGROUND)

        l_header = Label(self, text="Add resource", bg=constants.TITLE_BG, fg=constants.TITLE_FG, font=constants.TITLE_FONT)
        l_header.place(x=25, y=25)

        l_type = Label(self, text="Type:", bg=constants.HEADER_BG, fg=constants.HEADER_FG, font=constants.HEADER_FONT)
        l_type.place(x=25, y=80)

        self.type = tkinter.StringVar()
        c_type = ttk.Combobox(self, width=constants.COMBOBOX_WIDTH, font=constants.COMBOBOX_FONT, textvariable=self.type)
        c_type['values'] = (constants.STOCKS,
                            constants.CURRENCIES,
                            constants.CRYPTOCURRENCIES)
        c_type.current(0)
        c_type.place(x=140, y=80)

        l_resource = Label(self, text="Resource:", bg=constants.HEADER_BG, fg=constants.HEADER_FG, font=constants.HEADER_FONT)
        l_resource.place(x=25, y=120)

        self.e_resource = Entry(self, width=constants.ENTRY_WIDTH)
        self.e_resource.configure(font=constants.ENTRY_FONT)
        self.e_resource.place(x=140, y=120)

        l_quantity = Label(self, text="Quantity:", bg=constants.HEADER_BG, fg=constants.HEADER_FG, font=constants.HEADER_FONT)
        l_quantity.place(x=25, y=160)

        self.e_quantity = Entry(self, width=constants.ENTRY_WIDTH)
        self.e_quantity.configure(font=constants.ENTRY_FONT)
        self.e_quantity.place(x=140, y=160)

        l_price = Label(self, text="Price:", bg=constants.HEADER_BG, fg=constants.HEADER_FG, font=constants.HEADER_FONT)
        l_price.place(x=25, y=200)

        self.e_price = Entry(self, width=constants.ENTRY_WIDTH)
        self.e_price.configure(font=constants.ENTRY_FONT)
        self.e_price.place(x=140, y=200)

        b_add = Button(self, text='Add', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH,
                       command=lambda: self.add_resource())
        b_add.place(x=100, y=255)

        b_back = Button(self, text='Back', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH,
                        command=lambda: controller.show_frame('StartPage'))
        b_back.place(x=100, y=325)

    def add_resource(self):
        type = self.type.get()
        resource = self.e_resource.get()
        quantity = self.e_quantity.get()
        price = self.e_price.get()

        gui.wallet.add(type, resource, float(quantity), float(price))
        print(gui.wallet.resources)

        self.clear_text()

    def clear_text(self):
        self.e_resource.delete(0, 'end')
        self.e_quantity.delete(0, 'end')
        self.e_price.delete(0, 'end')
