from util.loggable import Loggable

class Script(Loggable):
    def __init__(self) -> None:
        super().__init__()
        self.Name = self.__class__.__name__
    
    def __reduce__(self):
        return (self.__class__, ())

    def run(self, simulationParams) -> None:
        pass