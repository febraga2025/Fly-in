from typing import List, Dict
from models.graph import MapGraph
from models.zone import Zone
from models.drone import Drone
from models.connections import Connection


class Simulation:
    def __init__(self, map_graph: MapGraph, nb_drones: int) -> None:
        self.map_graph: MapGraph = map_graph
        self.turn: int = 0
        self.drones: List[Drone] = []

        start_zone = self.map_graph.start_zone
        if not start_zone:
            msg = "The map does not have a defined starting zone."
            raise ValueError(msg)

        for i in range(1, nb_drones + 1):
            new_drone = Drone(f"D{i}", start_zone)
            self.drones.append(new_drone)

    def get_zone_occupancy(self, zone: Zone) -> int:
        count = 0
        for d in self.drones:
            if d.current_zone == zone or d.target_zone == zone:
                count += 1
        return count

    def run_autopilot_turn(self, gps: Dict[str, int]) -> None:
        self.turn += 1
        turn_outputs: List[str] = []

        # 1. OFFICIAL LANDING: Release drones that have completed
        # their flight time
        for drone in self.drones:
            if drone.target_zone and self.turn >= drone.arrival_turn:
                drone.finish_flight()

        # 2. ARRIVAL RADAR (Restricted): If the drone is on
        # the LAST turn of its flight
        for drone in self.drones:
            if (
                drone.target_zone and
                self.turn == (drone.arrival_turn - 1) and
                drone.flight_cost > 1
            ):
                turn_outputs.append(f"{drone.id}-{drone.target_zone.name}")

        # 3. CONNECTION RADAR: Count who is already flying on the roads
        # to avoid congestion
        conn_usage: Dict[Connection, int] = {}
        for drone in self.drones:
            if drone.is_flying(self.turn) and drone.active_connection:
                key = drone.active_connection
                conn_usage[key] = conn_usage.get(key, 0) + 1

        # 4. Filter who can move (Not flying and not at the end)
        drones_to_move = [
            d for d in self.drones
            if (
                not d.is_flying(self.turn) and
                d.current_zone != self.map_graph.end_zone
            )
        ]

        # 5. Decide the route
        for drone in drones_to_move:
            current = drone.current_zone
            if current is None:
                continue
            current_dist = gps.get(current.name, 999999)

            best_neighbor = None
            best_dist: float = 999999.0
            best_conn: Connection | None = None
            connection_used = ""

            for conn in self.map_graph.connections:
                if current in (conn.zone_a, conn.zone_b):
                    neighbor = conn.get_opposite_zone(current)

                    # Rule 1: Destination ZONE must have space
                    if (
                        neighbor.can_enter() and
                        self.get_zone_occupancy(neighbor) <
                        neighbor.max_drones
                    ):

                        # Rule 2: CONNECTION (Road) must have space
                        current_conn_usage = conn_usage.get(conn, 0)
                        if current_conn_usage < conn.max_link_capacity:

                            dist = gps.get(neighbor.name, 999999)
                            is_priority = (
                                neighbor.__class__.__name__ ==
                                "PriorityZone"
                            )
                            virtual_dist = (
                                dist - 0.1 if is_priority else dist
                            )

                            # Rule 3: Don't go backwards
                            if (
                                virtual_dist < best_dist and
                                dist <= current_dist
                            ):
                                best_dist = virtual_dist
                                best_neighbor = neighbor
                                best_conn = conn
                                connection_used = (
                                    f"{current.name}-{neighbor.name}"
                                )

            # 6. Apply movement and generate initial output
            if best_neighbor:
                cost = best_neighbor.get_movement_cost()
                drone.target_zone = best_neighbor
                drone.arrival_turn = self.turn + cost
                drone.flight_cost = cost
                drone.connection_name = connection_used
                drone.active_connection = best_conn
                drone.current_zone = None

                # Reserve the spot on the road right away
                if best_conn is not None:
                    conn_usage[best_conn] = (
                        conn_usage.get(best_conn, 0) + 1
                    )

                if cost == 1:
                    zone_str = best_neighbor.name
                    turn_outputs.append(f"{drone.id}-{zone_str}")
                else:
                    turn_outputs.append(f"{drone.id}-{connection_used}")
        print(" ".join(turn_outputs))

    def is_finished(self) -> bool:
        for drone in self.drones:
            if drone.current_zone != self.map_graph.end_zone:
                return False
        return True
