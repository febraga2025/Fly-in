import sys

from simulation_runner import run_text_simulation
from visualizer.replay import run_pygame_replay


def main() -> None:
    # 1. Verifica se o usuário passou o nome do mapa no terminal
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file.txt>")
        sys.exit(1)

    map_file = sys.argv[1]

    try:
        map_graph, turn_logs, history = run_text_simulation(map_file)

        for log_line in turn_logs:
            print(log_line)

        run_pygame_replay(map_graph, history, map_file)

    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
