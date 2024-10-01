import csv
from typing import List
from multiprocessing import Pool

from util.simulation_from_json import SimulationFromJson
from util.loggable import Loggable

class TrafficSimulator(Loggable):
    def __init__(self, 
            simulation_configs: List[str], 
            manifest: str = 'manifest.csv',
            simulation_count: int = 1,
            process_count: int = 1) -> None:
        super().__init__()
        self.process_count = process_count
        self.simulation_configs = [sim_config for sim_config in simulation_configs for _ in range(0, simulation_count)]
        self.manifest = manifest
        self.results = None

    # Run simulations
    def run(self) -> None:
        self.results = []
        if self.process_count > 1:
            self.log('Running simulations in parallel...')
            self._execute_multithreaded()
        else:
            self.log('Running simulations sequentially...')
            self._execute_singlethreaded()

        self.log('Simulations complete.')

        self.log('Generating manifest...')
        self._generate_manifest()
        self.log(f'Manifest saved to {self.manifest}')
    
    # Execute simulations sequentially
    def _execute_singlethreaded(self) -> None:
        for sim_config in self.simulation_configs:
            self.results.append(self._execute_simulation(sim_config))

    # Execute simulations in parallel
    def _execute_multithreaded(self) -> None:
        with Pool(processes=self.process_count) as pool:
            self.results = pool.map(self._execute_simulation, self.simulation_configs)

    # Execute a single simulation
    def _execute_simulation(self, simulation_json) -> None:
        self.log(f'Loading simulation from config {simulation_json}...')
        simulation = SimulationFromJson(simulation_json)
        self.log(f'Simulation loaded.')

        return simulation.run()

    def _generate_manifest(self) -> None:
        if self.results is None:
            raise RuntimeError('No results to generate manifest from.')
            return

        with open(self.manifest, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Id',
                'OutputDirectory',
                'Lambda',
                'Delta',
                'V_max',
                'd_min',
                'L_car',
                'L_track',
                'TimeStep',
                't_max',
                'LaneCount',
                'LaneVelocityWeights',
                'PassingModifier',
                'ImpatienceStep'])
            for sim_data in self.results:
                writer.writerow([
                    sim_data['Id'],
                    sim_data['OutputDirectory'], 
                    sim_data['Lambda'],  
                    sim_data['Delta'],   
                    sim_data['V_max'],   
                    sim_data['d_min'],   
                    sim_data['L_car'],   
                    sim_data['L_track'], 
                    sim_data['TimeStep'],
                    sim_data['t_max'],   
                    sim_data['LaneCount'],   
                    sim_data['LaneVelocityWeights'], 
                    sim_data['PassingModifier'], 
                    sim_data['ImpatienceStep']])