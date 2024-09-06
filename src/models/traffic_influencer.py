#####################
# DEPRACATED 9/2/24 #
#####################
# Remains in codebase in order to assist porting of legacy scripts to new model from JSON.
import warnings
from typing import List
from models.car import Car

class TrafficInfluencer:
    def __init__(self) -> None:
        warnings.warn(
            "TrafficInfluencer is deprecated and will be removed in a future version. "
            "Please update your code to use the new model from JSON.",
            DeprecationWarning,
            stacklevel=2)

    def update_status(self, t: float) -> None:
        pass
    
    def influence(self, cars: List[Car]) -> List[Car]:
        pass