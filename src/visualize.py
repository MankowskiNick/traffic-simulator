from argparse import ArgumentParser
from pathlib import Path
from util.visualizer import Visualizer
import uuid
import csv


SCRIPT_DIR = Path(__file__).resolve().parent

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
                        required=False,
                        help='Directory containing CSVs of simulation data. Overrides OutputDirectory from the manifest.')
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
    parser.add_argument('--start-time',
                        type=float,
                        default=None,
                        help='Simulation time to start visualizing from. Uses the closest recorded timestep at or before this value.'
    )
    return parser.parse_args()


def resolve_simulation_csv(manifest_path: Path, simulation_params: dict, directory: str | None) -> Path:
    filename = f"{simulation_params['Id']}.csv"

    if directory is not None:
        return Path(directory) / filename

    if 'OutputDirectory' not in simulation_params or simulation_params['OutputDirectory'] == '':
        raise ValueError("Manifest row does not include an OutputDirectory; pass --dir explicitly.")

    recorded = Path(simulation_params['OutputDirectory'])
    if recorded.is_absolute():
        candidates = [recorded / filename]
    else:
        candidates = [
            manifest_path.parent / recorded / filename,
            manifest_path.parent / 'raw' / filename,
            SCRIPT_DIR.parent / recorded / filename,
            Path.cwd() / recorded / filename,
        ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return candidates[0]

if __name__ == '__main__':
    args = parse_arguments()

    # Get the model parameters
    # Get simulation id
    simulation_id = str(args.id)

    # Read and extract model parameters from manifest file
    simulation_params = None
    manifest_path = Path(args.manifest)
    with open(manifest_path, 'r') as file:
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

    visualizer.load(resolve_simulation_csv(manifest_path, simulation_params, args.dir))
    if args.start_time is not None:
        visualizer.set_start_time(args.start_time)
    visualizer.run()
