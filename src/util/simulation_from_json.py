import json
from uuid import uuid4
from os import path, makedirs
from typing import List

from models.car import Car
from util.model import Model
from util.loggable import Loggable
from util.script import Script

class SimulationFromJson(Loggable):
    def __init__(self, json_file: str) -> None:
        super().__init__()

        # Assign a guid to act as a run id
        self.Id = uuid4()

        # Load JSON file
        self.log(f'Loading simulation from {json_file}')
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        # Model parameters
        self.log('Loading model parameters...')
        self.Lambda:                float = data.get('Lambda', 1)
        self.Delta:                 float = data.get('Delta', 0.0)
        self.V_max:                 float = data.get('V_max', 40.0)
        self.d_min:                 float = data.get('d_min', 7.5)
        self.L_car:                 float = data.get('L_car', 5.0)
        self.L_track:               float = data.get('L_track', 1000.0)
        self.TimeStep:              float = data.get('TimeStep', 0.05)
        self.t_max:                 float = data.get('t_max', 1000.0)
        self.LaneCount:             int = data.get('LaneCount', 1)
        self.OutputDirectory:       str = data.get('OutputDirectory', '')
        self.LaneVelocityWeights:   List[float] = data.get('LaneVelocityWeights', [1.0 for _ in range(0, self.LaneCount)])
        self.PassingModifier:       float = data.get('PassingModifier', 0.1)
        self.ImpatienceStep:        float = data.get('ImpatienceStep', 0.001)
        self.Collided:              bool = False

        # Configure pre run script
        preRunFile = data.get('PreRunScript', '')
        if preRunFile == '':
            raise RuntimeError('PreRunScript not supplied.')
        exec( open(preRunFile).read() )

        # Required to supply an instance of the pre run script
        if 'PreRunInstance' not in locals():
            raise RuntimeError("PreRunInstance not defined in pre run script.")
        self.PreRunScript: Script = locals()['PreRunInstance']

        # Configure post run script
        self.PostRunScript: Script = None
        # If supplied a post run script, configure it
        postRunFile = data.get('PostRunScript', '')
        if postRunFile != '':
            exec( open( postRunFile).read() ) 
            if 'PostRunInstance' not in locals():
                raise RuntimeError('PostRunInstance not defined in post run script.')
            self.PostRunScript:         PostRunScript = locals()['PostRunInstance']

        self.Cars = None
        self.log('Model parameters loaded.')

    def run(self) -> None:
        self.log(f'Initializing simulation run...')

        # Run pre request script, this is required to get the "cars" variable
        self.log(f"Running pre run script: {self.PreRunScript.Name}")
        self.PreRunScript.run(self)
        if self.PreRunScript.Cars is None:
            raise RuntimeError("Cars not defined in pre run script.")
        self.Cars = self.PreRunScript.Cars
        self.log(f"{self.PreRunScript.Name} ran successfully.")
        self.log(f'Loaded {len(self.Cars)} cars.')

        # Build model with parameters
        self.log('Building model...')
        self.model = Model(lbda=self.Lambda, 
                           start_time=0,
                           max_time=self.t_max,
                           collision_threshold=self.L_car,
                           time_step=self.TimeStep, 
                           track_length=self.L_track,
                           cars=self.Cars, 
                           lane_count=self.LaneCount,
                           lane_vmax_weights=self.LaneVelocityWeights,
                           passing_modifier=self.PassingModifier,)
        self.log('Model built.')

        # Evaluate model
        self.log('Evaluating model..')
        self.model.evaluate()
        self.log('Run completed.')

        self.Collided = self.model.collided

        # Run post run script
        if self.PostRunScript is not None:
            self.log(f"Running post run script: {self.PostRunScript.Name}")
            self.PostRunScript.run(self)
            self.log(f"{self.PostRunScript.Name} ran successfully")

        # Dump to csv
        self.log(f'Dumping model to {self.OutputDirectory}{self.Id}.csv...')
        self.dump_to_csv()
        self.log('Dump completed.')

        self.log('Simulation run complete.')

        # Return self so that the TrafficSimulator can generate a manifest
        return {
                'Id': self.Id,
                'OutputDirectory': self.OutputDirectory,
                'Lambda': self.Lambda,
                'Delta': self.Delta,
                'V_max': self.V_max,
                'd_min': self.d_min,
                'L_car': self.L_car,
                'L_track': self.L_track,
                'TimeStep': self.TimeStep,
                't_max': self.t_max,
                'LaneCount': self.LaneCount,
                'LaneVelocityWeights': self.LaneVelocityWeights,
                'PassingModifier': self.PassingModifier,
                'ImpatienceStep': self.ImpatienceStep
        }


    def dump_to_csv(self) -> None:
        # Check if the output directory exists
        if not path.exists(self.OutputDirectory):
            makedirs(self.OutputDirectory)
        self.model.dump(f'{self.OutputDirectory}{self.Id}.csv')
