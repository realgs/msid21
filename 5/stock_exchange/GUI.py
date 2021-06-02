from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox


class GUI:

    def __init__(self):
        self._type = "Currency"
        self._stock = "BIT"
        self._assets = []
        self._root = Tk()
        self._configure_root()
        self._create_labels()
        self._create_entries()
        self._add_radio_buttons()
        self._add_button()
        self._root.mainloop()

    def _configure_root(self):
        self._root.title("Wallet")
        self._root.geometry("530x400")
        self._root.configure(bg="#2a9d8f")
        self._root.iconbitmap("Images/icon.ico")
        self._root.resizable(False, False)

    def _create_labels(self):
        self._add_label("Enter asset name: ", 0, "name_label")
        self._add_label("Enter owned quantity: ", 1, "quantity_label")
        self._add_label("Enter average buy value: ", 2, "value_label")
        self._add_label("Choose asset type: ", 3, "type_label")
        self._add_label("Choose stock: ", 4, "stock_label")
        self._root.nametowidget("stock_label").grid_remove()

    def _add_label(self, text, row, name):
        label = Label(self._root, text=text, anchor='w', fg='#ECFDFA', name=name)
        label.config(width=24)
        label.config(font=("Bahnschrift Light", 12))
        label.configure(bg="#2a9d8f")
        label.grid(row=row, column=0, pady=(0, 10))

    def _create_entries(self):
        self._add_entry(0, "name_entry")
        self._add_entry(1, "quantity_entry")
        self._add_entry(2, "value_entry")

    def _add_entry(self, row, name):
        entry = Entry(self._root, width=50, name=name)
        entry.grid(row=row, column=1, pady=(0, 10))

    def _add_radio_buttons(self):
        style = ttk.Style()
        style.configure("Green.TRadiobutton", background="#2a9d8f", foreground="#ECFDFA",
                        font=('Bahnschrift Light', 12))
        type_frame = Frame(self._root, width=50, bg="#2a9d8f")
        type_frame.grid(row=3, column=1)
        ttk.Radiobutton(type_frame, text="Currency", variable=self._type, value="Currency", style="Green.TRadiobutton",
                        command=lambda: self._display_stocks(False)).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Crypto", variable=self._type, value="Crypto", style="Green.TRadiobutton",
                        command=lambda: self._display_stocks(True)).grid(row=0, column=2, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Other", variable=self._type, value="Other", style="Green.TRadiobutton",
                        command=lambda: self._display_stocks(False)).grid(row=0, column=3)

        stock_frame = Frame(self._root, width=50, bg="#2a9d8f", name="stock_frame")
        stock_frame.grid(row=4, column=1)
        ttk.Radiobutton(stock_frame, text="Bitbay", variable=self._stock, value="BIT", style="Green.TRadiobutton",
                        name="bitbay_radio").grid(row=0, column=1)
        ttk.Radiobutton(stock_frame, text="Bittrex", variable=self._stock, value="BTR", style="Green.TRadiobutton",
                        name="bittrex_radio").grid(row=0, column=2, padx=(20, 0))

        stock_frame.nametowidget("bitbay_radio").grid_remove()
        stock_frame.nametowidget("bittrex_radio").grid_remove()

    def _display_stocks(self, display):
        if display:
            self._root.nametowidget("stock_frame").nametowidget("bitbay_radio").grid()
            self._root.nametowidget("stock_frame").nametowidget("bittrex_radio").grid()
            self._root.nametowidget("stock_label").grid()
        else:
            self._root.nametowidget("stock_frame").nametowidget("bitbay_radio").grid_remove()
            self._root.nametowidget("stock_frame").nametowidget("bittrex_radio").grid_remove()
            self._root.nametowidget("stock_label").grid_remove()

    def _add_button(self):
        Button(self._root, text="Add asset", bg="#2F3D3B", fg="#ECFDFA", font=('Bahnschrift Light', 14),
               command=lambda: self._add_asset()).place(rely=1.0, relx=1.0, x=-5, y=-5, anchor=SE)

    def _add_asset(self):
        name = self._root.nametowidget("name_entry").get()
        quantity = self._root.nametowidget("quantity_entry").get()
        value = self._root.nametowidget("value_entry").get()

        if len([asset for asset in self._assets if asset["name"] == name]) != 0:
            messagebox.showerror("Error!", "Asset was already added to the wallet!")
            return
        if not self._is_positive_real(quantity):
            messagebox.showerror("Error!", "Quantity should be a positive, real number!")
            return
        if not self._is_positive_real(value):
            messagebox.showerror("Error!", "Value should be a positive, real number!")
            return

        if self._type == "Crypto":
            asset = {"name": name, "quantity": float(quantity), "avg_value": float(value), "type": self._type,
                     "stock": self._stock}
        else:
            asset = {"name": name, "quantity": float(quantity), "avg_value": float(value), "type": self._type}

        self._assets.append(asset)

    def _is_positive_real(self, value):
        try:
            val = float(value)
            return val > 0
        except ValueError:
            return False
