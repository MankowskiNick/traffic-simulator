from typing import List

class CarBase:
    def __init__(self, id: int) -> None:
        self.id = id
        self.pos = []
        self.velocity = []
        self.time = []
        self.lanes = []
        self.impatience = []
        self.time_step = 0.05
    
    # Get position at time t
    # Params:
    #   - t: time get get position at
    # Returns:
    #   - position of car at t
    def get_pos_at_time(self, t: float) -> float:
        return self.__get_at_time__(t, self.pos)

    # Get velocity at time t
    # Params:
    #   - t: time get velocity at
    # Returns:
    #   - velocity of car at t
    def get_velocity_at_time(self, t: float) -> float:
        return self.__get_at_time__(t, self.velocity)

    # Get headway at time t
    # Params:
    #   - t: time get headway at
    # Returns:
    #   - headway of car at t
    def get_headway_at_time(self, t: float, lane: int) -> float:
        if lane >= self.lane_count or lane < 0:
            return 0.0
        return self.__get_at_time__(t, self.headway[lane])

    # Get lane at time t
    # Params:
    #   - t: time get lane at
    # Returns:
    #   - lane of car at t
    def get_lane_at_time(self, t: float) -> float:
        return self.__get_at_time__(t, self.lanes)
    
    # Get impatience at time t
    # Params:
    #   - t: time get get impatience at
    # Returns:
    #   - impatience of car at t
    def get_impatience_at_time(self, t: float) -> float:
        return self.__get_at_time__(t, self.impatience)

    # Helper function for getting values at time
    # Params:
    #   - t: time to get attribute at
    #   - list: list that you are pulling values from
    # Returns:
    #   - float: list value at time t
    def __get_at_time__(self, t: float, list: List[any]) -> float:
        if t < 0:
            return list[0]
        i = int(t / self.time_step)
        if i >= len(list):
            return None
        return list[i]