# Room Organizer

This Python script optimizes furniture placement in a room using either Simulated Annealing or Beam Search algorithms. It takes a room configuration from a YAML file and outputs the optimized furniture layout.

## Features

- Two optimization algorithms: Simulated Annealing and Beam Search
- Customizable room configurations via YAML files
- Visualization of the final furniture placement
- Flexible command-line interface for easy usage

## Installation

1.  Install the required dependencies:
   ```
   pip install pyyaml matplotlib
   ```

2. Ensure you have the custom modules (`room.annealing`, `room.beam`, `room.functions`, `room.visualize`) in your project directory.

## Usage

Run the script using the following command:

```
python main.py -a <algorithm> -c <config_file> [options]
```

### Required Arguments

- `-a, --algorithm`: Choose the optimization algorithm (`annealing` or `beamsearch`)
- `-c, --config`: Path to the room configuration YAML file

### Optional Arguments

#### For Simulated Annealing:
- `-d, --duration`: Duration for annealing in minutes (default: 0.2)
- `--auto`: Automatically determine the annealing schedule based on the duration
- `--tmax`: Initial temperature for annealing (default: 5000)
- `--tmin`: Final temperature for annealing (default: 0.001)
- `--steps`: Number of steps for annealing (default: 10000)

#### For Beam Search:
- `-p, --population_size`: Population size for beam search (default: 10)
- `--tmax`: Initial temperature for annealing (default: 5000)
- `--max_generations`: Maximum number of generations for beam search (default: 1000)
- `--acceptable_error`: Acceptable error for beam search (default: 0)

## Examples

1. Run Simulated Annealing with default settings:
   ```
   python main.py -a annealing -c room.yaml
   ```

2. Run Beam Search with custom population size and temperature:
   ```
   python main.py -a beamsearch -c room.yaml -p 20 --tmax 50.0
   ```

3. Run Simulated Annealing with auto scheduling and longer duration:
   ```
   python main.py -a annealing -c room.yaml -d 5 --auto
   ```

## Output

The script will print the optimized furniture placement to the console and save a visualization of the final layout as 'final_furniture_placement.png' in the current directory.
