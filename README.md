# Traffic Simulation

This project simulates traffic flow using various parameters defined in a JSON file. The simulation can be run from the command line or through an integrated development environment (IDE) like Visual Studio Code.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Output](#output)
<!-- - [Contributing](#contributing) -->
<!-- - [License](#license) -->

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/MankowskiNick/traffic-simulator.git
    cd traffic-simulator
    ```

2. **Create a virtual environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

To configure the traffic simulation, you need to provide a JSON file containing the simulation parameters. Here is an example of a configuration file:

```json
{
    "Lambda": 1.0,
    "Delta": 0.00,
    "V_max": 40.0,
    "d_min": 7.5,
    "L_car": 5.0,
    "L_track": 1000.0,
    "TimeStep": 0.05,
    "t_max": 1000.0,
    "LaneCount": 2,
    "LaneVelocityWeights": [1.0],
    "PassingModifier": 0.2,
    "ImpatienceStep": 0.001,
    "OutputDirectory": "example-simulation/output/",
    "PreRunScript": "example-simulation/pre_run_script.py",
    "PostRunScript": "example-simulation/post_run_script.py"
}
```
### Model Parameters

The traffic simulation model uses various parameters to define the behavior of the simulated traffic flow. Most of these parameters are found in Newell's paper, however, there are a few that are not.  Here is a list of parameters not found in this paper:

- `L_car`: The length of each car in meters.
- `L_track`: The length of the simulated track in meters.
- `TimeStep`: The time step used in the simulation in seconds.
- `t_max`: The maximum simulation time in seconds.
- `LaneCount`: The number of lanes in the simulated track.
- `OutputDirectory`: Directory to output resulting simulation CSV files.
- `LaneVelocityWeights`: The weights assigned to each lane, these weights act as a multiplier for the `V_max` value for drivers in the lane corresponding to the list index.
- `PassingModifier`: The amount that driver impatience grows once passed by someone in an adjacent lane.
- `ImpatienceStep`: The amount that driver impatience increases/decreases per time step while headway in an adjacent lane is higher/lower than the current lane.
- `PreRunScript`: The path to the pre-run script file.
- `PostRunScript`: The path to the post-run script file.

These parameters can be adjusted in the configuration file to customize the behavior of the traffic simulation according to your specific requirements.

### Pre and Post Run Scripts

You can customize the behavior of the traffic simulation by providing pre-run and post-run scripts. These scripts must inherit from the `Script` class. An implementation of `PreRunScript` is required to configure cars properly, while an implementation of `PostRunScript` is entirely optional.

Both pre-run and post-run scripts must inherit from the `Script` class, which provides common functionality for running scripts. When creating implementations of pre-run and post-run scripts, you are required to accept a parameter `simulationParams`, which is of type `SimulationFromJson`, for the `run` method.  The `run` method will be called either immediately before a simulation is ran or immediately after, depending on how you pass it in the JSON. This allows you to pass up-to-date information regarding the simulations to these scripts.

In the run method of your pre-run script, you **must** instantiate a variable `self.Cars`, which is of type `List[Car]`.  This allows you to configure the cars present in the simulation.  Each car has a `tags` parameter that is a list, where you can add different tags for each car.  For example, if you want to mark a car as `aggressive`, then you can simply add the `aggressive` tag in the car.  These user defined tags are intended to give better control over how you are gathering data in the `PostRunScript`.

In order for these scripts to be properly ran by the simulator, you must provide an instance of them under the local variable `PreRunInstance` or `PostRunInstance`, depending on the type of script.  If you fail to define an instance, you will encounter a runtime error, since the simulator is unable to provide an instance of your script otherwise.

Make sure to adjust the paths to the actual locations of your script files.  It is recommended to store all simulation data(scripts, configuration JSON, and output figures) in a folder for each unique simulation.


Here is an example of how to create a pre-run script:

```python
class MyPreRunScript(Script):
    def run(self, simulationParams):
        self.log("Running pre run script...")
        self.Cars = [] 
        # Here, you need to define cars based on parameters coming in from the simulationParams JSON.

# Defining `PreRunInstance` to be an instance of your pre-run class is required
PreRunInstance = MyPreRunScript()
```

Similarly, here is an example of how to create a post-run script:

```python
class MyPostRunScript(Script):
    def run(self, simulationParams):
        self.log("Running post run script...")

        # Here, you may want to graph relevant results from the traffic simulation.

# Defining `PostRunInstance` to be an instance of your post-run class is required if you wish to have a post-run script.
PostRunInstance = MyPostRunScript()

```

To use these scripts in your configuration file, you can specify the paths to the script files:

```json
"PreRunScript": "/path/to/pre/run/script.py",
"PostRunScript": "/path/to/post/run/script.py"
```

In order to see a complete simulation example, please see the `example-simulation/` directory.

## Usage

### Arguments
- `--simulation-json`: **(Required)** One or more JSON files containing simulation parameters.
- `--manifest`: **Optional** Specify a manifest file.  Default is `manifest.csv`.
- `--simulation-count`: **(Optional)** Number of simulations to run per supplied config file.  Default is 1.
- `--process-count`: **(Optional)** Number of processes to use for running concurrent simulations. Increase value to allow simulations to run multithreaded.  Default is 1.

### Running the Simulation

To run the simulation, you can use the following command:

```sh
python simulator.py --simulation-json <path_to_json_file> [<additional_json_files>] [--simulation-count <count>] [--process-count <count>]
```

### Examples

1. **Run a single simulation with one JSON configuration file:**
```sh
python simulator.py --simulation-json sim_config.json
```

2. **Run a single simulation with a specified manifest.
```sh
python simulator.py --simulation-json sim_config.json --manifest my_manifest.csv
```


3. **Run multiple simulations with multiple JSON configuration files:**
```sh
python simulator.py --simulation-json sim_config1.json sim_config2.json
```

4. **Run 5 simulations using 4 processes:**
```sh
python simulator.py --simulation-json sim_config.json --simulation-count 5 --process-count 4
```

5. **Run 5 simulations 3 times each, using 4 processes:**
```sh
python simulator.py --simulation-json sim_config1.json sim_config2.json --simulation-count 5 --process-count 4
```

### Error Handling
If no JSON configuration files are provided, the application will raise a ValueError:
```sh
ValueError: Please provide at least one JSON configuration.
```


## Output

The traffic simulation program automatically dumps a CSV file containing output data for each simulation to the predefined output directory specified in the configuration JSON. This file can be used to analyze and visualize the results of the simulation.

To access the simulation output, you can find the CSV file in the folder specified in the configuration file under the `OutputDirectory` parameter.

Each simulation is assigned a UUID that acts as a simulation ID.  Each simulation will be stored in the directory `{OutputDirectory}/{simulation-uuid}.csv`.

In order to keep track of simulation outputs, this tool will produce a manifest file that can be used to see the parameters each simulation was ran with.  If you do not specify a manifest, the tool will automatically use `manifest.csv`, however this can be configured with the `--manifest` argument.  

Here is an example manifest produced by the tool:

| Id                                   | OutputDirectory            | Lambda | Delta | V_max | d_min | L_car | L_track | TimeStep | t_max | LaneCount | LaneVelocityWeights | PassingModifier | ImpatienceStep |
|--------------------------------------|----------------------------|--------|-------|-------|-------|-------|---------|----------|-------|-----------|---------------------|-----------------|----------------|
| 8d970802-de03-4c61-b12d-ea0307033106 | example-simulation/output/ | 1.0    | 0.0   | 40.0  | 7.5   | 5.0   | 1000.0  | 0.05     | 10.0  | 2         | [1.0]               | 0.2             | 0.001          |
| 1eeb834e-4640-4d18-9555-cc39d9fe4477 | example-simulation/output/ | 1.0    | 0.0   | 40.0  | 7.5   | 5.0   | 1000.0  | 0.05     | 10.0  | 2         | [1.0]               | 0.2             | 0.001          |
| 512fab2b-82a1-49e4-85ab-ee8d912af438 | example-simulation/output/ | 1.0    | 0.0   | 40.0  | 7.5   | 5.0   | 1000.0  | 0.05     | 10.0  | 2         | [1.0]               | 0.2             | 0.001          |
| 657acebb-e1fc-4a1d-a309-925a93858096 | example-simulation/output/ | 1.0    | 0.0   | 40.0  | 7.5   | 5.0   | 1000.0  | 0.05     | 10.0  | 2         | [1.0]               | 0.2             | 0.001          |