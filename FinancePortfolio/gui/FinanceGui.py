import json
import os
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

from FinancePortfolio.api.calculations import RESOURCE_TYPES, CONFIG_FILE, getTable, BASE_CURRENCY


class FinanceGui(tk.Frame):

    config_file = CONFIG_FILE

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.geometry = "1150x650"
        self.parent.geometry(self.geometry)
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self.createToolbar()
        self.createMenu()
        self.createMenuHelp()
        self.text = tk.StringVar()
        self.createStatusbar()
        self.createWorkingSpace()
        self.createStyles()
        self.parent.columnconfigure(0, weight=999)
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=9999)
        self.parent.rowconfigure(2, weight=1)
        self.working = None
        self.filename = None
        self.resources_dictionary = {'base_currency': BASE_CURRENCY[0],
                                     'pl_stock': [],
                                     'us_stock': [],
                                     'cryptocurrencies': [],
                                     'currencies': []}

    def newFile(self):
        self.createWorkingSpace()
        self.resources_dictionary = {'base_currency': BASE_CURRENCY[0],
                                     'pl_stock': [],
                                     'us_stock': [],
                                     'cryptocurrencies': [],
                                     'currencies': []}

    def openFile(self):
        directory = (os.path.dirname(self.filename) if self.filename is not None else '.')
        filename = tk.filedialog.askopenfilename(
            title='Open file',
            initialdir=directory,
            filetypes=[('Json files', '*.json')]
        )
        if filename:
            self.config_file = filename
            self.createWorkingSpace()

    def saveFile(self):
        filename = tk.filedialog.asksaveasfilename(
            title='Save file: '
        )
        if filename:
            createJsonFile(filename, self.resources_dictionary)

    def displayHelp(self):
        filename = 'covid_help.txt'
        if filename:
            os.system(r'notepad.exe ' + filename)

    def quit(self, event=None):
        reply = tk.messagebox.askyesno("End", "Do you really want to end?", parent=self.parent)
        if reply:
            self.parent.destroy()

    def createToolbar(self):
        self.toolbar_images = []
        self.toolbar = tk.Frame(self.parent)
        for image, command in (
                ("images/editdelete.gif", self.quit),
                ("images/filenew.gif", self.newFile),
                ("images/fileopen.gif", self.openFile),
                ("images/filesave.gif", self.saveFile)):
            image = os.path.join(os.path.dirname(__file__), image)
            try:
                image = tk.PhotoImage(file=image)
                self.toolbar_images.append(image)
                button = tk.Button(self.toolbar, image=image, command=command)
                button.grid(row=0, column=len(self.toolbar_images) - 1)
            except tk.TclError as err:
                print(err)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

    def createMenu(self):
        self.menubar = tk.Menu(self.parent)
        self.parent["menu"] = self.menubar
        fileMenu = tk.Menu(self.menubar)
        for label, command, shortcut_text, shortcut in (
                ("New...", self.newFile, "Ctrl+N", "<Control-n>"),
                ("Open...", self.openFile, "Ctrl+O", "<Control-o>"),
                ("Save as...", self.saveFile, "Ctrl+S", "<Control-s>"),
                (None, None, None, None),
                ("Quit...", self.quit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                                     command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menubar.add_cascade(label="File", menu=fileMenu, underline=0)

    def createMenuHelp(self):
        fileMenu = tk.Menu(self.menubar)
        for label, command, shortcut_text, shortcut in (
                ("Help", self.displayHelp, "Ctrl+H", "<Control-h>"),
                (None, None, None, None),
        ):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                                     command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menubar.add_cascade(label="Help", menu=fileMenu, underline=0)

    def createStatusbar(self):
        self.statusbar = Label(self.parent, textvariable=self.text, anchor=W)
        self.setStatusBar('Enter data...')
        self.statusbar.after(5000, self.clearStatusBar)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

    def setStatusBar(self, status_text):
        self.text.set(status_text)
        self.statusbar.update_idletasks()

    def clearStatusBar(self):
        self.text.set("")

    def createStyles(self):
        combostyle = ttk.Style()
        combostyle.theme_create('combostyle', parent='alt', settings={'TCombobox': {'configure': {
            'selectbackground': 'midnight blue', 'fieldbackground': 'gray80', 'background': 'gray'}}})
        combostyle.theme_use('combostyle')

        treestyle = ttk.Style()
        treestyle.configure("Treeview", background="black", foreground="white", fieldbackground="black")

    def createWorkingSpace(self):
        self.working = tk.Frame(self.parent, background='midnight blue')
        self.working.grid(row=1, column=0, columnspan=1, rowspan=1, sticky=NSEW)

        blank_column_0 = Label(self.working, text='\t', bg='midnight blue', fg='white')
        blank_column_0.grid(column=0, row=1)

        resources_type_label = Label(self.working, text='Type:', bg='midnight blue', fg='white')
        resources_type_label.grid(column=1, row=1, sticky=E)

        resource_type_var = tk.StringVar()
        resources_type_combobox = ttk.Combobox(self.working, width=15, textvariable=resource_type_var,
                                               values=RESOURCE_TYPES, state='readonly')
        resources_type_combobox.grid(column=2, row=1, sticky=W)

        owned_label = Label(self.working, text='Owned resources:', bg='midnight blue', fg='white')
        owned_label.grid(column=4, row=1, sticky=W)

        default_resources_label = Label(self.working, text='Default:', bg='midnight blue', fg='white')
        default_resources_label.grid(column=8, row=1, sticky=W)

        resource_name_label = Label(self.working, text='Name:', bg='midnight blue', fg='white')
        resource_name_label.grid(column=1, row=2, sticky=E)

        resource_name_entry = Entry(self.working, width=18, bg='gray80')
        resource_name_entry.grid(column=2, row=2, sticky=W)

        quantity_label = Label(self.working, text='Quantity:', bg='midnight blue', fg='white')
        quantity_label.grid(column=1, row=3, sticky=E)

        quantity_entry = Entry(self.working, width=18, bg='gray80')
        quantity_entry.grid(column=2, row=3, sticky=W)

        average_cost_label = Label(self.working, text='Average cost:', bg='midnight blue', fg='white')
        average_cost_label.grid(column=1, row=4, sticky=E)

        average_cost_entry = Entry(self.working, width=18, bg='gray80')
        average_cost_entry.grid(column=2, row=4, sticky=W)

        def getDataFromUser():
            resource_type = resources_type_combobox.get()
            resource_name = resource_name_entry.get()
            resource_quantity = float(quantity_entry.get())
            resource_average_cost = float(average_cost_entry.get())
            resource_info = resource_type, resource_name, resource_quantity, resource_average_cost

            self.resources_dictionary[resource_type].append({'symbol': resource_name, 'quantity': resource_quantity,
                                                             'average_price': resource_average_cost})
            if base_currency_combobox.get():
                self.resources_dictionary['base_currency'] = base_currency_combobox.get()

            resources_scrolledtext.insert(INSERT, resource_info)
            resources_scrolledtext.insert(INSERT, '\n')

        add_button = Button(self.working, text='Add', command=getDataFromUser, bg='gray80', width=15)
        add_button.grid(column=2, row=5, sticky=W)

        blank_row_6 = Label(self.working, height=1, bg='midnight blue')
        blank_row_6.grid(column=1, row=6)

        depth_label = Label(self.working, text='Depth:', bg='midnight blue', fg='white')
        depth_label.grid(column=1, row=6, sticky=E)

        percent_label = Label(self.working, text='%', bg='midnight blue', fg='white')
        percent_label.grid(column=2, row=6, sticky=EW)

        depth_entry = Entry(self.working, width=5, bg='gray80')
        depth_entry.grid(column=2, row=6, sticky=W)

        base_currency_label = Label(self.working, text='Base currency:', bg='midnight blue', fg='white')
        base_currency_label.grid(column=1, row=7, sticky=E)

        base_currency_var = tk.StringVar()
        base_currency_combobox = ttk.Combobox(self.working, width=15, textvariable=base_currency_var,
                                              values=BASE_CURRENCY, state='readonly')
        base_currency_combobox.grid(column=2, row=7, sticky=W)

        blank_row_8 = Label(self.working, height=1, bg='midnight blue')
        blank_row_8.grid(column=1, row=8)

        blank_column_3 = Label(self.working, text='\t', bg='midnight blue')
        blank_column_3.grid(column=3, row=1)

        blank_column_8 = Label(self.working, text='\t\t\t\t', bg='midnight blue', fg='white')
        blank_column_8.grid(column=8, row=1)

        resources_scrolledtext = ScrolledText(self.working, bg='black', fg='white', height=15, width=45)
        resources_scrolledtext.grid(column=4, row=2, columnspan=2, rowspan=5, sticky=N)

        default_resources_scrolledtext = ScrolledText(self.working, bg='black', fg='white', height=15, width=40)
        default_resources_scrolledtext.grid(column=8, row=2, columnspan=2, rowspan=5, sticky=N)

        file = open(self.config_file, 'r')
        lines = file.readlines()
        for line in lines:
            default_resources_scrolledtext.insert(INSERT, line)

        headings = ('Name', 'Quantity', 'Price(last transaction)', 'Value', 'Net value', 'Best exchange', 'Value %',
                    'Net value %', 'Best exchange %', 'Arbitrage')
        result_tree = ttk.Treeview(self.working, columns=headings, show='headings')

        for col in headings:
            result_tree.heading(col, text=col, anchor=W)

        result_tree.column(0, width=50)
        result_tree.column(1, width=100)
        result_tree.column(2, width=150)
        result_tree.column(3, width=70)
        result_tree.column(4, width=80)
        result_tree.column(5, width=100)
        result_tree.column(6, width=70)
        result_tree.column(7, width=80)
        result_tree.column(8, width=100)
        result_tree.column(9, width=200)
        result_tree.grid(row=9, column=1, columnspan=8)

        scrollbar_result = Scrollbar(self.working, orient=VERTICAL, command=result_tree.yview)
        result_tree.configure(yscrollcommand=scrollbar_result.set)
        scrollbar_result.grid(column=21, row=9, sticky=NS)

        blank_column_1 = Label(self.working, height=1, bg='midnight blue')
        blank_column_1.grid(column=1, row=10)

        def showInfo():
            depth = depth_entry.get()
            if depth:
                depth = int(depth_entry.get())
            else:
                depth = 10  # default value
            if len(resources_scrolledtext.get('1.0', 'end-1c')) == 0:
                info_table = getTable(self.config_file, depth)
            else:
                base_currency = base_currency_combobox.get()
                if not base_currency:
                    base_currency = 'USD'  # default value
                self.resources_dictionary['base_currency'] = base_currency
                createJsonFile('my_wallet', self.resources_dictionary)
                info_table = getTable('my_wallet.json', depth)

            for (name, quantity, price, value, net_value, best_exchange, value_depth, net_value_depth, best_exchange_2,
                 arbitrage) in info_table:
                result_tree.insert("", "end", values=(name, quantity, price, value, net_value, best_exchange,
                                                      value_depth, net_value_depth, best_exchange_2, arbitrage))
            self.clearStatusBar()

        show_button = Button(self.working, text='Show data',
                             command=lambda: [self.setStatusBar('Loading data...'), showInfo()], bg='gray80', width=10)
        show_button.grid(column=8, row=11, sticky=E)


def createJsonFile(filename, content):
    json_object = json.dumps(content, indent=4)
    with open(f'{filename}.json', "w", -1, "utf-8") as file:
        file.write(json_object)


if __name__ == '__main__':
    root = tk.Tk()
    root.iconbitmap('images/currency.ico')
    root.title('Finance Portfolio')
    app = FinanceGui(master=root)
    app.mainloop()
