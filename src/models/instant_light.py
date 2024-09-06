#####################
# DEPRACATED 9/2/24 #
#####################
# Remains in codebase in order to assist porting of legacy scripts to new model from JSON.
import warnings
from model.traffic_influencer import TrafficInfluencer
from model.car import Car
from typing import List

class InstantLight(TrafficInfluencer):
    def __init__(self, red_time: float, green_time: float, affected_car_id: int, start_red: bool = False) -> None:
        super().__init__()
        warnings.warn(
            "InstantLight is deprecated and will be removed in a future version. "
            "Please update your code to use the new model from JSON.",
            DeprecationWarning,
            stacklevel=2)
        self.red = start_red
        self.red_time = red_time
        self.green_time = green_time
        self.car_id = affected_car_id
        self.last_change_time = 0.0

    def update_status(self, t: float) -> None:
        if self.red and (t - self.last_change_time) % self.red_time == 0:
            self.red = False
            self.last_change_time = t
        elif not self.red and (t - self.last_change_time) % self.green_time == 0:
            self.red = True
            self.last_change_time = t
    
    def influence(self, cars: List[Car]) -> List[Car]:
        influenced_velocity = 0 if self.red else (cars[0].max_v / 2.0)

        for i in range(0, len(cars)):
            if cars[i].id == self.car_id:
                cars[i].fix_velocity(influenced_velocity)
        return cars