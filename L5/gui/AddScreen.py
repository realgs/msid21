import json
import os.path

from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

TYPES = ["us_stock", "pl_stock", "crypto", "currency"]
RED = (1, 0, 0, 0.8)
WALLET_FILE = os.path.dirname(__file__) + "/../configs/wallet.json"


# Resource adding screen
class AddScreen(Screen):
    def add(self):

        # User input basic data validation
        type = self.ids.type.text
        if type not in TYPES:
            self.ids.type.text = ""
            self.ids.type.hint_text_color = RED
            self.ids.type.hint_text = "invalid type"
            return

        symbol = self.ids.symbol.text

        try:
            price = float(self.ids.price.text)
        except ValueError:
            self.ids.price.text = ""
            self.ids.price.hint_text_color = RED
            self.ids.price.hint_text = "invalid price"
            return

        try:
            quantity = float(self.ids.quantity.text)
        except ValueError:
            self.ids.quantity.text = ""
            self.ids.quantity.hint_text_color = RED
            self.ids.quantity.hint_text = "invalid quantity"
            return

        base = self.ids.base.text

        resource = {
            "type": type,
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "base": base
        }

        # Writing to wallet file
        with open(WALLET_FILE, "r+") as file:
            data = json.load(file)
            data.append(resource)
            file.seek(0)
            json.dump(data, file, indent=4)

        # Clearing text inputs
        for ch in self.ids.add_layout.children:
            if isinstance(ch, TextInput):
                ch.text = ""
