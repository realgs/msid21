from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from gui.AddScreen import AddScreen
from gui.MainScreen import MainScreen


class WalletApp(App):
    def build(self):
        Window.size = (1100, 600)
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(AddScreen(name='add'))
        return self.sm


if __name__ == "__main__":
    WalletApp().run()
