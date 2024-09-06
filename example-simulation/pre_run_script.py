class PreRunScript(Script):
    def run(self, simulationParams) -> None:
        super().run(simulationParams)
        self.Cars = []
        self.NumCars = 10
        for i in range(0, self.NumCars):
            self.Cars.append(
                Car(
                    id = i + 1, 
                    reaction_time       = simulationParams.Delta, 
                    headway_threshold   = simulationParams.d_min, 
                    x_0                 = i * (simulationParams.L_track / self.NumCars), 
                    t_0                 = 0, 
                    h_0                 = simulationParams.LaneCount * (simulationParams.L_track / self.NumCars), 
                    max_v               = simulationParams.V_max, 
                    time_step           = simulationParams.TimeStep,
                    lane                = i % simulationParams.LaneCount,
                    lane_count          = simulationParams.LaneCount,
                    impatience_step     = simulationParams.ImpatienceStep
                )
            )
        self.Cars = sorted(self.Cars, key= lambda car: car.pos[-1], reverse=True)
        self.log(f"Successfully generated {self.NumCars} cars for simulation.")

PreRunInstance = PreRunScript()