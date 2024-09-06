class PostRunScript(Script):
    def run(self, simulationParams):
        self.log(f"{len(simulationParams.Cars)} cars found!")

PostRunInstance = PostRunScript()