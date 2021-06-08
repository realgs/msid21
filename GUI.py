from tkinter import *
import tkinter as tk

import Pocket


class GUI:
    def __init__(self, parent):
        parent.geometry('1500x700')
        self.root = parent
        self.root.title('Portfolio')
        self.frame = tk.Frame(parent)
        self.frame.grid()
        refreshButton = tk.Button((self.frame), text='Refresh', command=(self.fill))
        refreshButton.grid(row=0, column=0, sticky=N)

        message = tk.Label(self.frame, text='Percent value: ', font=('Arial', 10))
        message.grid(row=0, column=1, sticky=N)

        self.percentEntry = tk.Entry(self.frame)
        self.percentEntry.delete(0,END)
        self.percentEntry.insert(0, '5')
        self.percentEntry.grid(row=0, column=2, sticky=N)
        self.fill()

    def fill(self):
        percent = int(self.percentEntry.get())
        percent /= 100

        data = Pocket.prepareData(percent)
        self.clear(data)

        message = tk.Label((self.frame), text='Name of resource', font=('Arial', 10))
        message.grid(row=1, column=0, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Currency', font=('Arial', 10))
        message.grid(row=1, column=2, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Ammount', font=('Arial', 10))
        message.grid(row=1, column=1, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Last market price', font=('Arial', 10))
        message.grid(row=1, column=3, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Value', font=('Arial', 10))
        message.grid(row=1, column=4, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Part of value', font=('Arial', 10))
        message.grid(row=1, column=5, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Netto', font=('Arial', 10))
        message.grid(row=1, column=6, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Part netto', font=('Arial', 10))
        message.grid(row=1, column=7, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Where to sell', font=('Arial', 10))
        message.grid(row=1, column=8, padx=5, pady=5, sticky=N)

        message = tk.Label((self.frame), text='Best arbitrage opportunity', font=('Arial', 10))
        message.grid(row=1, column=9, padx=5, pady=5, sticky=N)

        rowCounter = 2
        for element in data:
            columnCounter = 0
            for info in element:
                message = tk.Label((self.frame), text=str(element[info]), font=('Arial', 10), bg='white')
                message.grid(row=rowCounter, column=columnCounter, padx=5, pady=5, sticky=N)

                columnCounter += 1
            rowCounter += 1

    def clear(self, data):
        rowCounter = 2
        for element in data:
            columnCounter = 0
            for info in element:
                message = tk.Label((self.frame), text='          ', font=('Arial', 10), bg='white')
                message.grid(row=rowCounter, column=columnCounter, padx=5, pady=5, sticky=N)

                columnCounter += 1
            rowCounter += 1