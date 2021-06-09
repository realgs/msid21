from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
import wallet

ROUND = 4
COLS = (
    'Type',
    'Symbol',
    'Price',
    'Quantity',
    'Sell rate',
    'Sell value',
    'Profit\n(post-tax)',
    'Recommended\nmarket',
    'Arbitrage'
)


# Main app screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        data = wallet.read_wallet()

        # Add resources to table
        for resource in data:
            for key, value in resource.items():
                if type(value) == float:
                    value = round(value, ROUND)

                if key == 'type':
                    self.ids.type.add_widget(Label(text=value, size_hint=(1, 0.06)))

                elif key == 'symbol':
                    self.ids.symbol.add_widget(Label(text=value, size_hint=(1, 0.06)))

                elif key == 'price':
                    self.ids.price.add_widget(Label(text=str(value), size_hint=(1, 0.06)))

                elif key == 'quantity':
                    self.ids.quantity.add_widget(Label(text=str(value), size_hint=(1, 0.06)))

    def appraise_wallet(self):
        try:
            percent = float(self.ids.percent_input.text)
        except ValueError:
            return
        if 0 <= percent <= 100:
            Window.set_system_cursor("wait")
            # Get appraisal
            data = wallet.appraise(percent / 100)
            sum_value = 0
            sum_profit = 0

            # Clear widgets
            for ch in self.ids.table.children:
                ch.clear_widgets()

            # Add labels
            for i in range(len(COLS)):
                self.ids.table.children[len(self.ids.table.children)-i-1].add_widget(Label(
                    text=f'[b]{COLS[i]}[/b]',
                    markup=True,
                    size_hint=(1, 0.08),
                    halign='center'
                ))


            # Add resources to table
            for resource in data:
                for key, value in resource.items():
                    if type(value) == float:
                        value = round(value, ROUND)

                    if key == 'type':
                        self.ids.type.add_widget(Label(text=value, size_hint=(1, 0.06)))

                    elif key == 'symbol':
                        self.ids.symbol.add_widget(Label(text=value, size_hint=(1, 0.06)))

                    elif key == 'price':
                        self.ids.price.add_widget(Label(text=str(value), size_hint=(1, 0.06)))

                    elif key == 'quantity':
                        self.ids.quantity.add_widget(Label(text=str(value), size_hint=(1, 0.06)))

                    elif key == 'base':
                        self.ids.base.text = f'[b]Base currency: {value}        Recources to sell: {percent}%[/b]'

                    elif key == 'sell_rate':
                        self.ids.sell_rate.add_widget(Label(text=str(value), size_hint=(1, 0.06)))

                    elif key == 'sell_value':
                        self.ids.sell_value.add_widget(Label(text=str(value), size_hint=(1, 0.06)))
                        sum_value += value

                    elif key == 'sell_profit':
                        self.ids.sell_profit.add_widget(Label(text=str(value), size_hint=(1, 0.06)))
                        sum_profit += value

                    elif key == 'market':
                        self.ids.market.add_widget(Label(text=value, size_hint=(1, 0.06)))

                    elif key == 'arbitrage':
                        self.ids.arbitrage.add_widget(Label(text=value, size_hint=(1, 0.2), halign='center'))

            sum_value = round(sum_value, ROUND)
            sum_profit = round(sum_profit, ROUND)
            self.ids.sell_value.add_widget(Label(text=f'[b]{sum_value}[/b]', markup=True, size_hint=(1, 0.07)))
            self.ids.sell_profit.add_widget(Label(text=f'[b]{sum_profit}[/b]', markup=True, size_hint=(1, 0.07)))

        else:
            self.ids.percent_input.text = ""
            self.ids.percent_input.hint_text = "0 - 100 %"
            self.ids.percent_input.hint_text_color = (1, 0, 0, 0.8)

        Window.set_system_cursor("arrow")
