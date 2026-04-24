from typing import Dict, List
from models.graph import MapGraph


def build_distance_map(map_graph: MapGraph) -> Dict[str, int]:
    """Reverse Dijkstra"""
    if not map_graph.end_zone:
        msg = "The map does not have a defined end zone."
        raise ValueError(msg)

    distances: Dict[str, int] = {
        name: 999999 for name in map_graph.zones.keys()
    }
    distances[map_graph.end_zone.name] = 0

    unvisited: List[str] = list(map_graph.zones.keys())

    while unvisited:
        current_name = min(
            unvisited, key=lambda name: distances[name]
        )

        if distances[current_name] == 999999:
            break
        unvisited.remove(current_name)
        current_zone = map_graph.get_zone(current_name)

        for connection in map_graph.connections:
            if current_zone in (connection.zone_a, connection.zone_b):
                neighbor = connection.get_opposite_zone(current_zone)

                if (
                    not neighbor.can_enter() or
                    neighbor.name not in unvisited
                ):
                    continue
                cost = current_zone.get_movement_cost()
                new_dist = distances[current_name] + cost

                if new_dist < distances[neighbor.name]:
                    distances[neighbor.name] = new_dist
    return distances
