import tkinter as tk
from tkinter import ttk

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

notebook.add(frame1, text='Portfolio')
notebook.add(frame2, text='Raport sprzedaży')
notebook.add(frame3, text='Tabela')

# FRAME 1*********************************************************************************************
entry1 = tk.Entry(frame1, bg='white', font=60)
entry2 = tk.Entry(frame1, bg='white', font=60)
entry3 = tk.Entry(frame1, bg='white', font=60)
entry1.place(relx=0, rely=0.8, relwidth=0.5, relheight=0.1)
entry2.place(relx=0, rely=0.7, relwidth=0.5, relheight=0.1)
entry3.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.1)

button = tk.Button(frame1, text="Add currency", font=60)
button.place(relx=0, rely=0.9, relwidth=1, relheight=0.1, anchor='nw')

label1 = tk.Label(frame1, text="This is a label", bg='white', font=60)
label1.place(relx=0, rely=0, relwidth=1, relheight=0.6)
label2 = tk.Label(frame1, text="Currency", bg='grey', font=60)
label2.place(relx=1, rely=0.9, relwidth=0.5, relheight=0.1, anchor='se')
label3 = tk.Label(frame1, text="Amount", bg='grey', font=60)
label3.place(relx=1, rely=0.8, relwidth=0.5, relheight=0.1, anchor='se')
label4 = tk.Label(frame1, text="Rate", bg='grey', font=60)
label4.place(relx=1, rely=0.7, relwidth=0.5, relheight=0.1, anchor='se')

# FRAME 2*********************************************************************************************

button2 = tk.Button(frame2, text="Write percentage", font=60)
button2.place(relx=0, rely=0.9, relwidth=0.5, relheight=0.1, anchor='nw')
Entry4 = tk.Entry(frame2, text="Currency", bg='white', font=60)
Entry4.place(relx=1, rely=1, relwidth=0.5, relheight=0.1, anchor='se')
label5 = tk.Label(frame2, text="This is a label", bg='white', font=60)
label5.place(relx=0, rely=0, relwidth=1, relheight=0.9)

# FRAME 3*********************************************************************************************

label6 = tk.Label(frame3, text="frame", bg='white', font=40)
label6.place(relx=0, rely=0, relwidth=1, relheight=1)

root.mainloop()