from tkinter import *
import constants


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background=constants.BACKGROUND)

        name = Label(self, text='CLIENT', bg='gray17', fg='DarkOrange2', font=('Helvetica', 58, 'bold'))
        name.place(x=110, y=50)

        b_keys = Button(self, text='Wallet', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH,
                        command=lambda: controller.show_frame('WalletPage'))
        b_keys.place(x=100, y=185)

        b_start = Button(self, text='Information', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH,
                         command=lambda: self.info())
        b_start.place(x=100, y=255)

        b_quit = Button(self, text='Quit', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH, command=controller.destroy)
        b_quit.place(x=100, y=325)

    def info(self):
        self.controller.delete_information_page()
        self.controller.add_information_page()
        self.controller.show_frame('InformationPage')
