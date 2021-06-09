import tkinter as tk


import gui.MainFrame as MainFrame


def main():
    root = tk.Tk()
    root.title("Portfolio inwestycyjne")
    root.minsize(500, 300)
    root.geometry('600x320')
    root.config(background='#6b7272')
    icon = tk.PhotoImage(file='img\dollar.png')
    root.iconphoto(False, icon)
    app = MainFrame.MainFrame(master=root)
    app.mainloop()
