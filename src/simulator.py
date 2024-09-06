from argparse import ArgumentParser
from typing import List

from util.traffic_simulator import TrafficSimulator

def parse_arguments():
    parser = ArgumentParser(description='Run a traffic simulation.')
    
    parser.add_argument('--simulation-json', 
                        type=str, 
                        nargs='+', 
                        required=True, 
                        help='JSON file(s) containing simulation parameters.')
    parser.add_argument('--simulation-count', 
                        type=int, 
                        default=1, 
                        help='Number of simulations to run.')
    parser.add_argument('--process-count', 
                        type=int,
                        default=1, 
                        help='Number of processes to use for running concurrent simulations.')
    parser.add_argument('--manifest',
                        type=str,
                        default='manifest.csv',
                        help='Output manifest file for keeping track of output runs.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    if args.simulation_json is None or len(args.simulation_json) == 0:
        raise ValueError('Please provide at least one JSON configuration.')

    # Run simulations
    main = TrafficSimulator(simulation_configs=args.simulation_json, 
        manifest=args.manifest,
        simulation_count=args.simulation_count, 
        process_count=args.process_count)
    main.run()