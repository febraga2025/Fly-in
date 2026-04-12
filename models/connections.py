from models.zone import Zone


class Connection:
    """Represents the two-way connection between two zones"""
    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int = 1) -> None:
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity

    def get_opposite_zone(self, zone: Zone) -> Zone:
        """Given one side of the connection, the other side returns"""
        if zone == self.zone_a:
            return self.zone_b
        elif zone == self.zone_b:
            return self.zone_a
        raise ValueError(f"The zone {zone.name} is "
                         "not part of this connection")

    def __repr__(self) -> str:
        return (f"Connection{self.zone_a.name} <-> {self.zone_b.name},"
                f"cap={self.max_link_capacity}")
