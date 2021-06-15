import tkinter as tk
from tkinter import ttk

import Raport
import Wallet

def add_currency(entry1, entry2, entry3, label1):
    rate = entry1.get()
    amount = entry2.get()
    currency = entry3.get()
    Wallet.add_currency_to_wallet(rate, amount, currency)
    label1['text'] = Wallet.get_money_info()

def raport(entry, label):
    Raport.make_raport(float(entry.get()))
    label['text'] = Raport.get_raport_string()

def create_arbitrage_table(label):
    possible_arbitrages = Wallet.check_arbitrage()
    if possible_arbitrages == []:
        label['text'] = "Currently there is no possibility to earn money with arbitrage"
    else:
        string_info = ""
        for item in possible_arbitrages:
            string_info += f"MARKET: {item[0]} EARNINGS: {item[1]} API1: {item[2]} API2: {item[3]} \n"
    label['text'] = string_info


root = tk.Tk()
root.geometry('800x800')
root.title("Moja giełda")

notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

frame1 = ttk.Frame(notebook, width=800, height=800)
frame2 = ttk.Frame(notebook, width=800, height=800)
frame3 = ttk.Frame(notebook, width=800, height=800)

frame1.pack(fill='both', expand=True)
frame2.pack(fill='both', expand=True)
frame3.pack(fill='both', expand=True)

notebook.add(frame1, text='Wallet')
notebook.add(frame2, text='Sell Raport')
notebook.add(frame3, text='Arbitrage Info')

# FRAME 1*********************************************************************************************
entry1 = tk.Entry(frame1, bg='white', font=60)
entry2 = tk.Entry(frame1, bg='white', font=60)
entry3 = tk.Entry(frame1, bg='white', font=60)
entry1.place(relx=0, rely=0.8, relwidth=0.5, relheight=0.1)
entry2.place(relx=0, rely=0.7, relwidth=0.5, relheight=0.1)
entry3.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.1)

label1 = tk.Label(frame1, text=Wallet.get_money_info(), bg='white', font=60, anchor='nw', justify=tk.LEFT)
label1.place(relx=0, rely=0, relwidth=1, relheight=0.6)
label2 = tk.Label(frame1, text="Rate", bg='grey', font=60)
label2.place(relx=1, rely=0.9, relwidth=0.5, relheight=0.1, anchor='se')
label3 = tk.Label(frame1, text="Amount", bg='grey', font=60)
label3.place(relx=1, rely=0.8, relwidth=0.5, relheight=0.1, anchor='se')
label4 = tk.Label(frame1, text="Currency", bg='grey', font=60)
label4.place(relx=1, rely=0.7, relwidth=0.5, relheight=0.1, anchor='se')

button = tk.Button(frame1, text="Add currency", font=60, command=lambda: add_currency(entry1, entry2, entry3, label1))
button.place(relx=0, rely=0.9, relwidth=1, relheight=0.1, anchor='nw')

# FRAME 2*********************************************************************************************

entry4 = tk.Entry(frame2, text="Currency", bg='white', font=60)
entry4.place(relx=1, rely=1, relwidth=0.5, relheight=0.1, anchor='se')
label5 = tk.Label(frame2, bg='white', font=("Arial", 10), anchor='w', justify=tk.LEFT)
label5.place(relx=0, rely=0, relwidth=1, relheight=0.9)
button2 = tk.Button(frame2, text="Write percentage", font=60, command=lambda: raport(entry4, label5))
button2.place(relx=0, rely=0.9, relwidth=0.5, relheight=0.1, anchor='nw')

# FRAME 3*********************************************************************************************

label6 = tk.Label(frame3, bg='white', font=40)
label6.place(relx=0, rely=0, relwidth=1, relheight=1)
button2 = tk.Button(frame3, text="Check arbitrages", font=60, command=lambda: create_arbitrage_table(label6))
button2.place(relx=0, rely=0.9, relwidth=1, relheight=0.1, anchor='nw')

root.mainloop()