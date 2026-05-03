from __future__ import annotations
import sys

import io
from contextlib import redirect_stdout
from typing import List, Optional, Tuple

from algorithms.pathfinding import build_distance_map
from models.connections import Connection
from models.graph import MapGraph
from models.zone import Zone
from parse import parse_map
from simulation import Simulation


DroneSnapshot = Tuple[
    str,
    Optional[Zone],
    Optional[Zone],
    int,
    Optional[Connection],
    int,
]
TurnSnapshot = Tuple[int, List[DroneSnapshot]]


def _capture_simulation_state(simulation: Simulation) -> List[DroneSnapshot]:
    """Create a snapshot of the current drone states."""
    snapshots: List[DroneSnapshot] = []
    for drone in simulation.drones:
        snapshots.append(
            (
                drone.id,
                drone.current_zone,
                drone.target_zone,
                drone.arrival_turn,
                drone.active_connection,
                drone.flight_cost,
            )
        )
    return snapshots


def run_text_simulation(
    map_file: str,
) -> Tuple[MapGraph, List[str], List[TurnSnapshot]]:
    """Run the full simulation and collect text
    output plus replay snapshots."""
    map_graph, total_drones = parse_map(map_file)
    gps = build_distance_map(map_graph)
    simulation = Simulation(map_graph, total_drones)

    turn_logs: List[str] = []
    history: List[TurnSnapshot] = []

    while not simulation.is_finished():
        history.append(
            (simulation.turn, _capture_simulation_state(simulation))
        )

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            simulation.run_autopilot_turn(gps)  # flag here

        raw_lines = [line.strip() for line in buffer.getvalue().splitlines()]
        move_lines = [line for line in raw_lines if line.startswith("D")]
        # CAP_LINE HERE
        turn_line = move_lines[-1] if move_lines else ""

        if turn_line:
            print(turn_line)
            turn_logs.append(turn_line)
        """ # SHOW_CAPACITY
            if "--capacity-info" in sys.argv:
                # 1. Processando a capacidade das Zonas[cite: 1]
                z_cap = []
                for z in map_graph.zones.values():
                    # Ignoramos hubs com capacidade "infinita" (start/end)
                    if z.max_drones < 1000:
                        occ = simulation.get_zone_occupancy(z)
                        z_cap.append(f"Zone {z.name}: {occ}/{z.max_drones} drones")

                # 2. Processando a capacidade das Conexões[cite: 1]
                c_cap = []
                for c in map_graph.connections:
                    # Contamos quantos drones estão voando nesta conexão agora
                    usage = 0
                    for d in simulation.drones:
                        if d.active_connection == c and d.is_flying(simulation.turn):
                            usage += 1
                    c_cap.append(f"Conn {c.zone_a.name}-{c.zone_b.name}: {usage}/{c.max_link_capacity} used")

                # 3. Imprimindo o resultado formatado[cite: 1]
                print(f"  [CAPACITY] {', '.join(z_cap + c_cap)}") """
        if simulation.is_finished() and not turn_line:
            simulation.turn -= 1
            break

    return map_graph, turn_logs, history
