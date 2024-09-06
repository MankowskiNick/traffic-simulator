

import csv
from numpy import arange, exp, arctan
from random import random
from typing import List

from const.param import *
from models.car import Car
from models.traffic_light import *
from models.traffic_influencer import TrafficInfluencer
from util.loggable import Loggable

def is_integer_multiple(a: float, b: float) -> bool:
    if b == 0:
        raise ValueError("The divisor cannot be null.")
    quotient = a / b
    return abs(quotient - round(quotient)) < ERROR_MARGIN

class Model(Loggable):
    def __init__(self,
                lbda: float, 
                start_time: float,
                max_time: float,
                collision_threshold: float,
                time_step: float, 
                cars: List[Car],
                lights: List[TrafficLight] = [],
                influencers: List[TrafficInfluencer] = [],
                lane_count: int = 1,
                track_length: float = 100,
                lane_change_frequency: float = 1.0,
                lane_vmax_weights: List[float] = [],
                passing_modifier = 0.1
                ) -> None:
        super().__init__()
        # Assert clean data
        for c in cars:
            assert is_integer_multiple(c.reaction_time, time_step), f"ERROR: reaction time must be an integer multiple of time step({c.reaction_time % time_step})"

        # Parameters for model
        self.lbda = float(lbda)
        self.time_step = float(time_step)
        self.start_time = float(start_time)
        self.max_time = float(max_time)
        self.num_cars = len(cars)
        self.cars = cars
        self.track_length = float(track_length)
        self.collision_threshold = float(collision_threshold)
        self.passing_modifier = float(passing_modifier)

        self.lane_count = lane_count
        self.lane_change_frequency = lane_change_frequency

        self.lights = lights
        self.influencers = influencers

        self.running = True     # running the simulation?
        self.collided = False
        self.collided_ids = []

        self.lane_changes = []

        self.end_time = self.max_time - self.time_step

        self.lane_vmax_weights = lane_vmax_weights if len(lane_vmax_weights) == lane_count else [1.0 for _ in range(0, lane_count)]

    # Run simulation
    def evaluate(self) -> None:
        # Step through time and use Euler's method to calculate positon
        for t in arange(self.start_time, self.max_time, self.time_step):

            # Stop if we indicate the model should no longer be running
            if not self.running:
                return
            
            for light in self.lights:
                light.update_status(t)
            for inf in self.influencers:
                inf.update_status(t)
                self.cars = inf.influence(self.cars)

            # Sort cars based on position to ensure the "next" car is always the one directly in front
            self.cars = sorted(self.cars, key=lambda car: car.pos[-1], reverse=True)

            # Update lane of cars
            self.get_lane(t)

            # Update headway of cars
            self.get_headway(t)

            # Get velocity of the cars
            self.get_velocity(t)

            # Update position of cars
            self.get_position(t)

            # Update time of cars
            self.save_time(t)

    # Parameters:
    #   - t: current time
    def save_time(self, t: float) -> None:
        for i in range(0, self.num_cars):
            self.cars[i].time.append(t)

    def get_car_passing_impatience(self, i: int, t: float):
        impatience = 0.0

        target_car = self.cars[i]
        r_t = self.cars[i].reaction_time

        lane = self.cars[i].get_lane_at_time(t - r_t)
        prev_lane = self.cars[i].get_lane_at_time(t - r_t - self.time_step)

        # Only consider constant lanes
        if lane != prev_lane:
            return 0

        target_pos = self.cars[i].get_pos_at_time(t - r_t)
        target_pos_prev = self.cars[i].get_pos_at_time(t - r_t - self.time_step)
        if target_pos - target_pos_prev < 0:
            target_pos += self.track_length

        for j in range(0, len(self.cars)):
            if i == j:
                continue

            check_car = self.cars[j]

            # Only consider lanes immediately next to the target car
            if abs(check_car.get_lane_at_time(t - r_t) - lane) != 1:
                continue

            c_pos = check_car.get_pos_at_time(t - r_t)
            c_pos_prev = check_car.get_pos_at_time(t - r_t - self.time_step)

            if c_pos - c_pos_prev < 0:
                c_pos += self.track_length

            prev_diff = target_pos_prev - c_pos_prev
            cur_diff = target_pos - c_pos

            if prev_diff > 0 and cur_diff < 0:
                impatience += self.passing_modifier
        return impatience

    def process_lane_change(self, t: float, i: int, cur_lane: int, left_headway: float, right_headway) -> int:

        can_go_left = cur_lane > 0
        can_go_right = cur_lane < self.lane_count - 1

        # TODO: this solution may not work for large reaction times
        # Prop.: For an n lane traffic system, we only need to check n - 1 cars to see if lane changing will cause a collision from behind/front
        # Cor.: For an n lane traffic system, we only need to check 2n - 2 cars to see if lane changing will cause a collision
        # Using this to speed up lane changing.  May have to stop doing this when facotring in larger reaction times
        for j in range(i - self.lane_count + 1, i + self.lane_count): 
            if i == j:
                continue
            car = self.cars[j % self.num_cars]
            car_headway = (car.get_pos_at_time(t - self.cars[i].reaction_time) - self.cars[i].get_pos_at_time(t - self.cars[i].reaction_time)) % self.track_length
            car_lane = car.get_lane_at_time(t - self.cars[i].reaction_time)

            if car_headway < self.cars[i].headway_threshold or car_headway >= self.track_length - self.cars[i].headway_threshold: 
                if car_lane == cur_lane - 1:
                    can_go_left = False
                if car_lane == cur_lane + 1:
                    can_go_right = False
        probability = 1 - pow(1 - ((2 / PI) * arctan(self.cars[i].get_impatience_at_time(t))), self.time_step)
        probability_to_change = 0 if probability < 0 else probability
        random_draw = random()

        # If the probability allows, attempt a lane change
        if random_draw <= probability_to_change:

            # If we can go left and it is preferable, go left
            if can_go_left and left_headway >= right_headway:
                cur_lane -= 1
                self.cars[i].impatience[-1] = 0
                self.lane_changes.append({
                    'car_id': self.cars[i].id,
                    'current_lane': cur_lane + 1,
                    'target_lane': cur_lane,
                    'time': t
                })
            # Otherwise, go right if it is preferable
            elif can_go_right:
                cur_lane += 1
                self.cars[i].impatience[-1] = 0
                self.lane_changes.append({
                    'car_id': self.cars[i].id,
                    'current_lane': cur_lane - 1,
                    'target_lane': cur_lane,
                    'time': t
                })
        
        # Return the lane decided
        return cur_lane

    def get_lane(self, t: float) -> None:
        for i in range(0, self.num_cars):
            # Get current lane of car
            cur_lane = self.cars[i].get_lane_at_time(t)
            impatience = self.cars[i].get_impatience_at_time(t)
            
            # Get headway in current lane, as well as the headway if the car was in the right and left lane
            headway = self.cars[i].get_headway_at_time(t - self.cars[i].reaction_time, cur_lane)
            left_headway = self.cars[i].get_headway_at_time(t - self.cars[i].reaction_time, cur_lane - 1)
            right_headway = self.cars[i].get_headway_at_time(t - self.cars[i].reaction_time, cur_lane + 1)

            if self.lane_count > 1:
                # If the headway in the other lanes is larger, then the driver becomes less patient
                if left_headway > headway or right_headway > headway:
                    impatience += self.cars[i].impatience_step

                # Otherwse, the driver becomes more patient
                elif impatience > 0:
                    impatience -= self.cars[i].impatience_step

                # Factor in passing cars to impatience
                impatience += self.get_car_passing_impatience(i, t)
            
            # Add impatience to the car
            self.cars[i].impatience.append(impatience)
            
            # Process possible lane change
            cur_lane = self.process_lane_change(t, i, cur_lane, left_headway, right_headway)
            self.cars[i].lanes.append(cur_lane)

    # Parameters:
    #   - t: current time
    def get_headway(self, t: float) -> None:
        # Get headway for each car
        for i in range(0, self.num_cars):

            # Get cur lane
            cur_lane = self.cars[i].get_lane_at_time(t)

            # headways[lane] = headway for that current lane
            headways = [INF for _ in range(0, self.lane_count)]
            seen_lanes = []

            for j in range(i - 1, i - self.num_cars + 1, -1):
                car = self.cars[j % self.num_cars]
                lane = car.get_lane_at_time(t)

                if lane in seen_lanes:
                    continue

                headway = (car.get_pos_at_time(t) - self.cars[i].get_pos_at_time(t)) % self.track_length

                headways[lane] = headway
                seen_lanes.append(lane)

                # Check for collision
                if headway < self.collision_threshold and lane == cur_lane:
                    self.log(f"Collision between car #{self.cars[i].id} and car #{self.cars[j].id} at time t={t}.\n    Car #{self.cars[i].id}: pos={self.cars[i].get_pos_at_time(t)}; vel={self.cars[i].velocity[-1]}\n    Car #{self.cars[j].id}: pos={car.get_pos_at_time(t)}; vel={self.cars[j].velocity[-1]}")
                    self.running = False
                    self.collided = True
                    self.collided_ids += [self.cars[i].id, self.cars[j].id]
                    self.end_time = t - self.time_step

                if len(seen_lanes) == self.lane_count:
                    break

            # Store the headway values in the car
            for lane, headway in enumerate(headways):
                self.cars[i].headway[lane].append(headway)

    # Parameters:
    #   - t: current time
    def get_position(self, t: float) -> None:
        for i in range(0, self.num_cars):
            old_car_pos = self.cars[i].pos[-1]
            vel = self.cars[i].velocity[-1]
            stepsize = vel * self.time_step
            new_car_pos = (old_car_pos + stepsize) % self.track_length
            self.cars[i].pos.append(new_car_pos)

    # Parameters:
    #   - t: current time
    def get_velocity(self, t: float) -> None:
        # Get current velocity of each car
        for i in range(0, self.num_cars):

            # If the velocity is fixed, then disregard further computation and add velocity for this time step
            if self.cars[i].fixed_velocity is not None:
                self.cars[i].velocity.append(self.cars[i].fixed_velocity)
                continue

            cur_lane = self.cars[i].get_lane_at_time(t - self.cars[i].reaction_time)
            dist_to_next = self.cars[i].get_headway_at_time(t - self.cars[i].reaction_time, cur_lane)

            # If an influencers is close enough, then allow it to be treated as a "next car" in terms of headway
            for light in self.lights:

                # Get distance to light
                dist_to_light = (light.pos - self.cars[i].get_pos_at_time(t - self.cars[i].reaction_time)) % self.track_length

                # If the light is red, then treat the red light as a car in the distance calculation
                if dist_to_light < dist_to_next and light.status == LightStatus.RED:
                    dist_to_next = dist_to_light

                # If the light is yellow, see if the perceived distance to travel is greater than the distance
                # to the light.  If it is, keep driving and ignore the light.  Otherwise, treat it as a stop.
                elif dist_to_light < dist_to_next and light.status == LightStatus.YELLOW:
                    perceived_velocity = self.cars[i].get_velocity_at_time(t - self.cars[i].reaction_time)
                    time_left = light.yellow_time - t - light.last_change_time
                    carryover_dist = perceived_velocity * time_left
                    if carryover_dist < dist_to_light:
                        dist_to_next = dist_to_light

            lane = self.cars[i].get_lane_at_time(t - self.cars[i].reaction_time)

            # Get velocity of car using Newell's equation
            vel = (self.cars[i].max_v * self.lane_vmax_weights[lane]) - (self.cars[i].max_v * self.lane_vmax_weights[lane]) * exp((-1 * self.cars[i].lbda / (self.lane_vmax_weights[lane] * self.cars[i].max_v)) * ((dist_to_next - self.cars[i].headway_threshold)))

            # Velocity cannot be < 0
            if vel < 0:
                vel = 0

            self.cars[i].velocity.append(vel)

    def dump(self, filename="data/run.csv") -> None:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Car ID', 'Time', 'Position', 'Velocity', 'Impatience', 'Lane'] + [f'Headway to Lane {lane}' for lane in range(0, self.lane_count)])
            for car in self.cars:
                for i in range(1, len(car.pos)):
                    writer.writerow([
                        car.id, 
                        round(car.time[i], 4), 
                        round(car.pos[i], 6), 
                        round(car.velocity[i], 6), 
                        round(car.impatience[i], 6),
                        car.lanes[i]] + [headway[i] for headway in car.headway])