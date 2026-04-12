from typing import List, Dict, Optional
from models.graph import MapGraph
from models.zone import Zone
from models.drone import Drone

# Tabela de Cores ANSI para o Terminal
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "orange": "\033[38;5;208m",
    "brown": "\033[38;5;94m",
    "purple": "\033[38;5;129m",
    "gray": "\033[90m",
    "reset": "\033[0m"
}

def colorize(text: str, color_name: Optional[str]) -> str:
    if color_name and color_name.lower() in COLORS:
        return f"{COLORS[color_name.lower()]}{text}{COLORS['reset']}"
    return text

class Simulation:
    def __init__(self, map_graph: MapGraph, nb_drones: int) -> None:
        self.map_graph: MapGraph = map_graph
        self.turn: int = 0
        self.drones: List[Drone] = []

        start_zone = self.map_graph.start_zone
        if not start_zone:
            raise ValueError("The map does not have a defined starting zone.")
        
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

        # 1. POUSO OFICIAL: Libera os drones que já completaram o tempo de voo
        for drone in self.drones:
            if drone.target_zone and self.turn >= drone.arrival_turn:
                drone.finish_flight()

        # 2. RADAR DE CHEGADA (Restricted): Se o drone está no ÚLTIMO turno do voo dele
        for drone in self.drones:
            if drone.target_zone and self.turn == (drone.arrival_turn - 1) and drone.flight_cost > 1:
                colored_zone = colorize(drone.target_zone.name, drone.target_zone.color)
                turn_outputs.append(f"{drone.id}-{colored_zone}")

        # 3. RADAR DE CONEXÕES: Conta quem já está voando nas estradas para não engarrafar
        conn_usage = {}
        for drone in self.drones:
            if drone.is_flying(self.turn) and drone.active_connection:
                conn_usage[drone.active_connection] = conn_usage.get(drone.active_connection, 0) + 1

        # 4. Filtra quem pode se mover (Quem não está voando e não chegou no fim)
        drones_to_move = [
            d for d in self.drones
            if not d.is_flying(self.turn) and d.current_zone != self.map_graph.end_zone
        ]

        # 5. Decide a rota
        for drone in drones_to_move:
            current = drone.current_zone
            current_dist = gps.get(current.name, 999999)
            
            best_neighbor = None
            best_dist = 999999
            best_conn = None
            connection_used = ""

            for conn in self.map_graph.connections:
                if current in (conn.zone_a, conn.zone_b):
                    neighbor = conn.get_opposite_zone(current)

                    # Regra 1: ZONA destino tem que ter espaço
                    if neighbor.can_enter() and self.get_zone_occupancy(neighbor) < neighbor.max_drones:
                        
                        # Regra 2: CONEXÃO (Estrada) tem que ter espaço
                        current_conn_usage = conn_usage.get(conn, 0)
                        if current_conn_usage < conn.max_link_capacity:
                            
                            dist = gps.get(neighbor.name, 999999)
                            virtual_dist = dist - 0.1 if neighbor.__class__.__name__ == "PriorityZone" else dist

                            # Regra 3: Não andar para trás
                            if virtual_dist < best_dist and dist <= current_dist:
                                best_dist = virtual_dist
                                best_neighbor = neighbor
                                best_conn = conn
                                connection_used = f"{current.name}-{neighbor.name}"

            # 6. Aplica o movimento e gera o output inicial
            if best_neighbor:
                cost = best_neighbor.get_movement_cost()
                drone.target_zone = best_neighbor
                drone.arrival_turn = self.turn + cost
                drone.flight_cost = cost
                drone.connection_name = connection_used
                drone.active_connection = best_conn 
                drone.current_zone = None 

                # Reserva a vaga na estrada na mesma hora
                conn_usage[best_conn] = conn_usage.get(best_conn, 0) + 1

                if cost == 1:
                    colored_zone = colorize(best_neighbor.name, best_neighbor.color)
                    turn_outputs.append(f"{drone.id}-{colored_zone}")
                else:
                    turn_outputs.append(f"{drone.id}-{connection_used}")

        # O PRINT OFICIAL DA MOULINETTE (sem o 'if' para garantir que os turnos vazios apareçam)
        print(" ".join(turn_outputs))

    def is_finished(self) -> bool:
        for drone in self.drones:
            if drone.current_zone != self.map_graph.end_zone:
                return False
        return True