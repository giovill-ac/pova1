import yaml
import argparse

from room.annealing import FurniturePlacementAnnealer
from room.beam import FurniturePlacementBeamSearch
from room.functions import Furniture, Door
from room.visualize import draw_room, print_room


def load_room_config(config_file):
    """Load room configuration from a YAML file."""
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    room_width = config["room_width"]
    room_height = config["room_height"]
    doors = [
        Door(door["name"], door["position"], door["length"], door["is_horizontal"])
        for door in config["doors"]
    ]
    furniture_dict = {
        furniture["name"]: Furniture(
            furniture["name"],
            furniture["width"],
            furniture["height"],
            furniture["color"],
            furniture.get("preferred_on_wall"),
            furniture.get("nearby_furniture", []),
            furniture.get("front", None),
        )
        for furniture in config["furnitures"]
    }
    return room_width, room_height, doors, furniture_dict


def run_annealing(room_width, room_height, doors, furniture_dict, duration, tmax=5000, tmin=0.001, steps=10000, auto=False):
    """Run simulated annealing to find the best furniture placement."""
    annealer = FurniturePlacementAnnealer(
        room_width, room_height, doors, furniture_dict
    )
    if auto:
        schedule = annealer.auto(minutes=duration)
    else:
        schedule = {'tmax': tmax, 'tmin': tmin, 'steps': steps, 'updates': 100}
    print("\nAnnealing schedule:", schedule)
    annealer.set_schedule(schedule)
    best_state, best_energy = annealer.anneal()
    return best_state


def run_beam_search(
    room_width,
    room_height,
    doors,
    furniture_dict,
    population_size,
    temperature,
    max_generations,
    acceptable_error,
):
    """Run beam search to find the best furniture placement."""
    beam_search = FurniturePlacementBeamSearch(
        room_width,
        room_height,
        doors,
        furniture_dict,
        population_size=population_size,
        temperature=temperature,
        max_generations=max_generations,
        acceptable_fitness=acceptable_error
    )
    best_state = beam_search.run()
    return best_state


def main():
    parser = argparse.ArgumentParser(
        description="Furniture Placement Optimization using Annealing or Beam Search"
    )

    # Argument for selecting the algorithm (annealing or beam search)
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=["annealing", "beamsearch"],
        required=True,
        help="Choose optimization algorithm: 'annealing' or 'beamsearch'",
    )

    # Argument for specifying the room configuration file
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the room configuration YAML file",
    )

    # Annealing-specific arguments
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=0.2,
        help="Duration for annealing in minutes (default: 0.2)",
    )

    # Beam search-specific arguments
    parser.add_argument(
        "-p",
        "--population_size",
        type=int,
        default=10,
        help="Population size for beam search (default: 10)",
    )
    parser.add_argument(
        "--max_generations",
        type=int,
        default=1000,
        help="Maximum number of generations for beam search (default: 1000)",
    )
    parser.add_argument(
        "--acceptable_error",
        type=float,
        default=0,
        help="Acceptable error for beam search (default: 0)",
    )
    parser.add_argument(
        "--auto",
        action='store_true',
        help="Automatically determine the annealing schedule based on the duration",
    )
    parser.add_argument(
        "--tmax",
        type=float,
        default=5000,
        help="Initial temperature for annealing (default: 5000)",
    )
    parser.add_argument(
        "--tmin",
        type=float,
        default=0.001,
        help="Final temperature for annealing (default: 0.001)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10000,
        help="Number of steps for annealing (default: 10000)",
    )
    args = parser.parse_args()

    # Load the room configuration
    room_width, room_height, doors, furniture_dict = load_room_config(args.config)

    # Run the chosen optimization algorithm
    if args.algorithm == "annealing":
        print("Running Simulated Annealing...")
        best_state = run_annealing(
            room_width, room_height, doors, furniture_dict, args.duration, args.tmax, args.tmin, args.steps, args.auto
        )
    elif args.algorithm == "beamsearch":
        print("Running Beam Search...")
        best_state = run_beam_search(
            room_width,
            room_height,
            doors,
            furniture_dict,
            args.population_size,
            args.tmax,
            args.max_generations,
            args.acceptable_error,
        )

    # Output results
    print_room(furniture_dict, best_state)
    draw_room(room_width, room_height, doors, furniture_dict, best_state)
    from room.functions import objective
    print("Objective function value:", objective(best_state, furniture_dict, room_width, room_height, doors))
    print("Plot saved as 'final_furniture_placement.png'")


if __name__ == "__main__":
    main()
