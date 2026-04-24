from typing import Optional


class Zone:
    """Abstract class for all zones"""

    def __init__(self, name: str, x: int, y: int, max_drones: int = 1,
                 color: Optional[str] = None) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.max_drones: int = max_drones
        self.color: Optional[str] = color

        self.is_start: bool = False
        self.is_end: bool = False

    def get_movement_cost(self) -> int:
        raise NotImplementedError(
            "Subclasses must implement get_movement"
        )

    def can_enter(self) -> bool:
        """Checks the zone (blocked returns false)"""
        return True

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.name}, max={self.max_drones})"
        )


class PriorityZone(Zone):
    def get_movement_cost(self) -> int:
        return 1


class NormalZone(Zone):
    def get_movement_cost(self) -> int:
        return 1


class RestrictedZone(Zone):
    def get_movement_cost(self) -> int:
        return 2


class BlockedZone(Zone):
    def get_movement_cost(self) -> int:
        return 999

    def can_enter(self) -> bool:
        return False
