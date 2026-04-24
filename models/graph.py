from typing import Dict, List, Optional
from models.zone import Zone
from models.connections import Connection


class MapGraph:
    """Graph that stores all the zones and connections of the file."""

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            msg = f"Zone {zone.name} already exists in the graph"
            raise ValueError(msg)
        self.zones[zone.name] = zone
        if zone.is_start:
            self.start_zone = zone
        if zone.is_end:
            self.end_zone = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise KeyError(f"Zone '{name}' not found in map")
        return self.zones[name]
