import sys
from parse import parse_map
from simulation import Simulation
from algorithms.pathfinding import build_distance_map

def main() -> None:
    # 1. Verifica se o usuário passou o nome do mapa no terminal
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file.txt>")
        sys.exit(1)

    map_file = sys.argv[1]

    try:
        # 2. Roda o nosso Parser
        my_map, total_drones = parse_map(map_file)
        
        # 3. Calcula o GPS (Dijkstra)
        gps = build_distance_map(my_map)
        
        # 4. Inicia a Simulação
        sim = Simulation(my_map, total_drones)
        
        # Vamos imprimir a configuração inicial para debug
        print(f"Map: {map_file} loaded. Total Drones: {total_drones}")
        
        
        # 5. O Loop Automático
        max_turns = 150 # Limite de segurança
        while not sim.is_finished() and sim.turn < max_turns:
            sim.run_autopilot_turn(gps)
            
            
        if sim.is_finished():
            print(f"\nSUCCESS! All drones arrived in {sim.turn} turns! 🎉")
        else:
            print(f"\nTIMEOUT! Simulation stopped after {max_turns} turns.")
            
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == '__main__':
    main()