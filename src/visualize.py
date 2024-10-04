from argparse import ArgumentParser
from typing import List
from util.visualizer import Visualizer
import uuid
import csv

def parse_arguments():
    ## visualizer --manifest /path/to/manifest.csv --directory /path/to/dir/ --id 4f74ba7e-f753-425b-ab5c-1794f1caf5cc
    # python3 traffic-simulator/src/visualize.py --manifest stability-test/manifest.csv --dir stability-test/output/ --id c9db361e-6e07-4b56-947b-357aeb1dccd7
    parser = ArgumentParser(description='Run a traffic simulation.')
    
    parser.add_argument('--manifest', 
                        type=str,
                        required=True, 
                        help='JSON file(s) containing simulation parameters.')
    parser.add_argument('--dir',
                        type=str,
                        required=True,
                        help='Directory containing CSVs of simulation data.')
    parser.add_argument('--id',
                        type=uuid.UUID,
                        required=True,
                        help='ID of the simulation to visualize in the manifest.csv')
    parser.add_argument('--screen-size',
                        type=int,
                        required=False,
                        nargs='+',
                        help='Screen size in the form "width height".'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    if args.dir[-1] != '/':
        raise ValueError(f"Invalid directory: {args.dir} (perhaps missing a closing '/'?)")

    # Get the model parameters
    # Get simulation id
    simulation_id = str(args.id)

    # Read and extract model parameters from manifest file
    with open(args.manifest, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Id'] == simulation_id:
                simulation_params = row
                break
    if simulation_params is None:
        raise ValueError(f"Simulation ID {simulation_id} not found in the manifest.")

    # Get screen size from argument
    screenwidth, screenheight = 800,600
    if args.screen_size is not None:
        if len(args.screen_size) != 2:
            raise ValueError("Invalid screen-size parameter.  Must supply exactly 2 values, width and height.")
        screenwidth = args.screen_size[0]
        screenheight = args.screen_size[1]

    # Assuming Visualizer is used to visualize the simulation
    visualizer = Visualizer(
        screenwidth, screenheight,
        float(simulation_params['L_track']),
        100,
        int(simulation_params['LaneCount']),
        float(simulation_params['L_car']))

    visualizer.load(f'{args.dir}{simulation_id}.csv')
    visualizer.run()
