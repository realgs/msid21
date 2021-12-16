from tkinter import *
import start_page
import wallet_page
import information_page
import wallet

wallet = wallet.Wallet()

class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        print(wallet.resources) # ----- -- -- - -- - -
        self.title('Client')
        self.resizable(width=False, height=False)
        self.container = Frame(self)
        self.geometry('500x410')
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (start_page.StartPage, wallet_page.WalletPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('StartPage')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def add_information_page(self):
        frame = information_page.InformationPage(parent=self.container, controller=self)
        self.frames['InformationPage'] = frame
        self.frames['InformationPage'].grid(row=0, column=0, sticky='nsew')

    def delete_information_page(self):
        self.frames.pop('InformationPage', None)
