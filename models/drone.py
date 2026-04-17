from typing import Optional

from models.connections import Connection
from models.zone import Zone


class Drone:
    def __init__(self, drone_id: str, start_zone: Zone) -> None:
        self.id: str = drone_id
        self.current_zone: Optional[Zone] = start_zone

        self.target_zone: Optional[Zone] = None
        self.arrival_turn: int = 0
        self.flight_cost: int = 0
        self.connection_name: str = ""
        self.active_connection: Optional[Connection] = None

    def is_flying(self, current_turn: int) -> bool:
        return (
            self.target_zone is not None
            and current_turn < self.arrival_turn
        )

    def finish_flight(self) -> None:
        self.current_zone = self.target_zone
        self.target_zone = None
        self.arrival_turn = 0
        self.flight_cost = 0
        self.connection_name = ""

    def __repr__(self) -> str:
        return f"Drone({self.id})"
