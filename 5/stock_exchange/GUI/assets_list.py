from tkinter import *
from tkinter import ttk

class AssetsList(Toplevel):
    def __init__(self, **kw):
        super().__init__()
        self._assets = kw['root'].assets
        self._base_currency = kw['root'].base_currency
        self._configure_root()
        self._create_canvas()
        self._add_slider()
        self._list_assets()
        self.mainloop()

    def _create_canvas(self):
        Canvas(self, name="canvas", bg="#2a9d8f", bd=0, highlightthickness=0, relief='ridge').pack(side=LEFT, fill=BOTH, expand=1)

    def _configure_root(self):
        self.title("Wallet")
        self.geometry("530x240+900+500")
        self.configure(bg="#2a9d8f")
        self.iconbitmap("../Images/icon.ico")
        self.resizable(False, False)

    def _list_assets(self):
        for asset in self._assets:
            text = "{} {} - purchase rate {} {}".format(asset["quantity"], asset["name"], asset["avg_value"],
                                                        self._base_currency)
            label = Label(self.nametowidget("canvas").nametowidget("frame"), text=text, anchor='w', fg='#ECFDFA')
            label.config(width=36)
            label.config(font=("Bahnschrift Light", 12))
            label.configure(bg="#2a9d8f")
            label.pack()

    def _add_slider(self):
        style = ttk.Style()
        scrollbar = ttk.Scrollbar(self.nametowidget("canvas"), orient=VERTICAL, command=self.nametowidget("canvas").yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.nametowidget("canvas").configure(yscrollcommand=scrollbar.set)
        self.nametowidget("canvas").bind('<Configure>', lambda e: self.nametowidget("canvas").configure(scrollregion=self.nametowidget("canvas").bbox("all")))
        self.nametowidget("canvas").create_window((0, 0), window=Frame(self.nametowidget("canvas"), name="frame"), anchor="nw")
