#####################
# DEPRACATED 9/2/24 #
#####################
# Remains in codebase in order to assist porting of legacy scripts to new model from JSON.
import warnings
from model.model import *
import numpy as np
import uuid
import matplotlib.pyplot as plt
from model.traffic_influencer import TrafficInfluencer
from model.traffic_light import TrafficLight

class ModelDriver():
    def __init__(self,
                t_reaction: float,
                v_max: float,
                h_min: float,
                d_min: float,
                l_track: float,
                time_step: float,
                cars: List[Car],
                lbda: float = 1,
                traffic_lights: List[TrafficLight] = [],
                traffic_influencers: List[TrafficInfluencer] = [],
                lane_count: int = 1,
                dump_file: str = '',
                lane_vmax_weights: List[float] = [],
                passing_modifier = 0.1
                ) -> None:

        warnings.warn(
            "ModelDriver is deprecated and will be removed in a future version. "
            "Please update your code to use the new model from JSON.",
            DeprecationWarning,
            stacklevel=2)

            
        # UNITS:
        #   - time: seconds
        #   - distance: meters
        #   - velocity: meters/second

        # Parameters
        self.reaction_time = t_reaction # Seconds until driver reacts. TODO: find a paper that gives a realistic value.  this was based on a google search.
        self.speed_limit = v_max # 40 m/s is roughly 90 mph, this is above a typical highway speed limit to account for people speeding
        self.min_headway = h_min # Does this sound realistic? roughly 10 feet between cars in a traffic jam
        self.time_step = time_step # time step
        self.collision_threshold = d_min # minimum distance that will be considered a collision.  This acts as an analog for car size.

        # These parameters are pretty self explanatory
        self.track_length = l_track 
        self.num_cars = len(cars)
        self.cars = cars

        # Number of lanes
        self.lane_count = lane_count

        # Weighted vmax per lane. This gives the affect of giving a bias to certain lanes.abs
        # Should be a vector that is the size of the number of lanes, default is all values set to 1.0
        self.lane_vmax_weights = lane_vmax_weights
        
        # Lambda - controls acceleration based on headway.  The slope of the graph from Newell's 
        # paper detailing velocity vs headway
        self.lbda = lbda

        # Amount that the impatience will increase when passed by another car
        self.passing_modifier =  passing_modifier

        # Dump file - where will the simulation data be dumped? Empty string => don't save simulation datas
        self.dump_file = dump_file

        # Traffic lights and other influencers
        self.lights = traffic_lights
        self.influencers = traffic_influencers

    def run(self, t_0: float, t_max: float) -> None:
        # Build model with parameters
        self.model = Model(lbda=self.lbda, 
                           start_time=t_0,
                           max_time=t_max,
                           collision_threshold=self.collision_threshold,
                           time_step=self.time_step, 
                           cars=self.cars, 
                           lights=self.lights,
                           influencers=self.influencers,
                           track_length=self.track_length,
                           lane_count=self.lane_count,
                           lane_vmax_weights=self.lane_vmax_weights,
                           passing_modifier=self.passing_modifier)

        # Evaluate model
        self.model.evaluate()

        # Dump to csv
        if self.dump_file != '':
            self.model.dump(f'data/{self.dump_file}')

    def display_vel(self):
        # We have to have a model to display
        assert self.model is not None, "ERROR: No model generated."

        # Clear plot
        plt.clf()

        # Plot each car
        for i, c in enumerate(self.model.cars):
            if i > 5:
                break
            plt.plot(c.time[1:], c.velocity[1:], label=f"Car #{c.id}")#, color=c.color)

        # Label plot
        plt.xlabel('Time')
        plt.ylabel('Velocity')
        plt.title('Velocity vs Time')
        # plt.xlim(self.model.start_time, self.model.max_time)
        # plt.ylim(0, 40)
        plt.legend()
        #plt.savefig(f'figures/rt-{self.reaction_time}/velocity_plot.png')
        plt.show()

    def display_pos(self):
        # We have to have a model to display
        assert self.model is not None, "ERROR: No model generated."

        # Clear plot
        plt.clf()

        # Plot each car
        for c in self.model.cars:
            plt.plot(c.time[1:], c.pos[1:], label=f"Car #{c.id}")#, color=c.color)

        # Label plot
        plt.xlabel('Time')
        plt.ylabel('Position')
        plt.title('Position vs Time')
        # plt.xlim(self.model.start_time, self.model.max_time)
        # plt.ylim(0, 200)
        plt.legend()
        #plt.savefig(f'figures/rt-{self.reaction_time}/pos_plot.png')
        plt.show()

    def display_headway(self):
        # We have to have a model to display
        assert self.model is not None, "ERROR: No model generated."

        # Clear plot
        plt.clf()

        # Plot each car
        for c in self.model.cars:
            plt.plot(c.time[1:], c.headway[1:], label=f"Car #{c.id}")#, color=c.color)

        # Label plot
        plt.xlabel('Time')
        plt.ylabel('Headway')
        plt.title('Headway vs Time')
        # plt.xlim(self.model.start_time, self.model.max_time)
        # plt.ylim(0, 50)
        plt.legend()
        #plt.savefig(f'figures/rt-{self.reaction_time}/headway_plot.png')
        plt.show()

    def get_deltan(self) -> List:
        cars_per_lane = []
        for t in arange(self.model.start_time, self.model.max_time, self.model.time_step):
            lane_counts = [0 for _ in range(0, self.lane_count)]
            for car in self.model.cars:
                lane = car.get_lane_at_time(t)
                lane_counts[lane] += 1
            cars_per_lane.append(lane_counts)

        delta_n = [max(lane_counts) - min(lane_counts) for lane_counts in cars_per_lane]
        return delta_n