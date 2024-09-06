class Loggable:
    def __init__(self):
        # Get the title of the child class
        self.title = self.__class__.__name__

    def log(self, message: str) -> None:
        print(f'[{self.title}] {message}')