from abc import ABC, abstractmethod

class ExampleAbstractClass(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._version = "1.0.0"

    @abstractmethod
    def do_something(self):
        pass

    def version(self):
        return sefl._version
