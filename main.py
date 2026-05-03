import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from simulation_runner import run_text_simulation
from visualizer.replay import run_pygame_replay


def main() -> None:
    # 1. Check if user passed the map file name in terminal
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file.txt>")
        sys.exit(1)

    map_file = sys.argv[1]
    use_viz = "--visual" in sys.argv
    # show_cap = "--capacity-info" in sys.argv
    # capacity
    try:
        map_graph, _,history = run_text_simulation(map_file)

        #for log_line in turn_logs:
        #    print(log_line)
        if use_viz:
            run_pygame_replay(map_graph, history, map_file)

    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
