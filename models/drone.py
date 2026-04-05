from zone import Zone


class Drone:
    def __init__(self, id: str, current_zone: Zone):
        self.id: str = id
        self.current_zone: Zone = current_zone
        self.destination_zone: Zone | None = None  # Começa sem destino
        self.arrival_turn: int = 0

    def set_mission(self, destination: Zone, current_turn: int):
        self.destination_zone = destination
        cost = destination.get_cost()
        self.arrival_turn = current_turn + cost
        
        # Sai da zona atual para começar o voo
        if self.current_zone:
            self.current_zone.current_drones.remove(self)
            self.current_zone = None 

    def is_flying(self, current_turn: int) -> bool:
        return current_turn < self.arrival_turn

    def complete_mission(self):
        # O pouso: destino vira zona atual
        self.current_zone = self.destination_zone
        self.destination_zone = None
        self.arrival_turn = 0
        # Entra na lista da nova zona
        if self.current_zone:
            self.current_zone.current_drones.append(self)