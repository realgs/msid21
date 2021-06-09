from PyQt6.QtWidgets import QWidget

class View:
    def __init__(self, widgetStack):
        self.__stack = widgetStack
        self.widget = QWidget(widgetStack)
        widgetStack.addWidget(self.widget)

    def setup(self):
        pass

    def show(self):
        self.__stack.setCurrentWidget(self.widget)
        self.__stack.adjustSize()

