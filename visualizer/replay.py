from __future__ import annotations

import pygame
from typing import List, Optional, Tuple

from models.connections import Connection
from models.drone import Drone
from models.graph import MapGraph
from models.zone import Zone
from visualizer.vizu import Visualizador


DroneSnapshot = Tuple[
    str,
    Optional[Zone],
    Optional[Zone],
    int,
    Optional[Connection],
    int,
]
TurnSnapshot = Tuple[int, List[DroneSnapshot]]


def _build_replay_drones(
    snapshot: List[DroneSnapshot],
    map_graph: MapGraph,
) -> List[Drone]:
    """Rebuild temporary drones for the visual replay."""
    drones_temp: List[Drone] = []
    for d_id, cur, tar, arr, conn, cost in snapshot:
        initial_zone = cur or tar or map_graph.start_zone
        if initial_zone is None:
            raise ValueError("Replay snapshot has no valid initial zone.")

        drone = Drone(d_id, initial_zone)
        drone.current_zone = cur
        drone.target_zone = tar
        drone.arrival_turn = arr
        drone.active_connection = conn
        drone.flight_cost = cost
        drones_temp.append(drone)
    return drones_temp


def run_pygame_replay(
    map_graph: MapGraph,
    history: List[TurnSnapshot],
    map_file: str,
) -> None:
    """Open a pygame window to browse the simulation replay."""
    pygame.init()
    visualizer = Visualizador()
    screen = pygame.display.set_mode((visualizer.largura, visualizer.altura))
    pygame.display.set_caption(f"Fly-in Simulation: {map_file}")
    clock = pygame.time.Clock()

    frame_index = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_RIGHT
                    and frame_index < len(history) - 1
                ):
                    frame_index += 1
                elif event.key == pygame.K_LEFT and frame_index > 0:
                    frame_index -= 1

        turn_number, snapshot = history[frame_index]
        drones_temp = _build_replay_drones(snapshot, map_graph)

        screen.fill((44, 62, 80))
        visualizer.draw_mapa(screen, map_graph.zones, map_graph.connections)
        visualizer.draw_drones(screen, drones_temp, turn_number)
        text_turn = visualizer.fonte.render(
            f"Turno Atual: {turn_number}",
            True,
            (255, 255, 255),
        )
        screen.blit(text_turn, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
