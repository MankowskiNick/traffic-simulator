from typing import List
# from const.param import *
from models.carbase import CarBase

# Container for car information
class Car(CarBase):
    def __init__(self,
                id: int,
                reaction_time: float,
                headway_threshold: float,
                x_0: float,
                t_0: float,
                h_0: float,
                max_v: float,
                time_step: float,
                lane: int = 0,
                lane_count: int = 1,
                impatience_step: float = 0.001,
                lbda: float = 1.0,
                color: str = 'red',
                ) -> None:
        self.id = id
        self.reaction_time = reaction_time
        self.headway_threshold = headway_threshold
        self.x_0 = x_0
        self.t_0 = t_0
        self.max_v = max_v

        self.time_step = time_step
        self.time = [t_0]
        self.velocity = [0]
        self.pos = [x_0]
        self.headway = [[h_0] for i in range(0, lane_count)]
        self.total_dist = 0

        self.lanes = [lane]
        self.lane_count = lane_count

        self.lbda = lbda

        self.fixed_velocity = None

        self.color = color

        self.impatience = [0.0]
        self.impatience_step = impatience_step

        self.tags = []


        ######################
        # DEPRACATED 9/30/24 #
        # Replaced by 'tags' #
        ######################
        self.aggressive = False



    #####################
    # DEPRACATED 9/5/24 #
    #####################
    # Fix velocity to the given v
    # Params:
    #   - v: new velocity to fix to
    def fix_velocity(self, v: float) -> None:
        self.fixed_velocity = v