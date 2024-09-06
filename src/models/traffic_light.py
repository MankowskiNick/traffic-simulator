#####################
# DEPRACATED 9/2/24 #
#####################
# Remains in codebase in order to assist porting of legacy scripts to new model from JSON.
import warnings
from enum import Enum

class LightStatus(Enum):
    RED = 1
    YELLOW = 2
    GREEN = 3

class TrafficLight:
    def __init__(self, green_time: float, yellow_time: float, red_time: float, pos: float, status: LightStatus = LightStatus.YELLOW) -> None:
        warnings.warn(
            "TrafficLight is deprecated and will be removed in a future version. "
            "Please update your code to use the new model from JSON.",
            DeprecationWarning,
            stacklevel=2)

        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.status = LightStatus.YELLOW
        self.pos = pos
        self.last_change_time = 0.0
        self.light_size = 0

    def update_status(self, t: float) -> None:
        if self.status == LightStatus.RED and (t - self.last_change_time) % self.red_time == 0:
            self.status = LightStatus.GREEN
            self.last_change_time = t
        elif self.status == LightStatus.YELLOW and (t - self.last_change_time) % self.yellow_time == 0:
            self.status = LightStatus.RED 
            self.last_change_time = t
        elif self.status == LightStatus.GREEN and (t - self.last_change_time) % self.green_time == 0:
            self.status = LightStatus.YELLOW
            self.last_change_time = t