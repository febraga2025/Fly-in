from abc import ABC, abstractmethod


class Zone(ABC):
    def __init__(self, name: str, x: int, y: int, max_capacity: int, color: str):
        self.name = name
        self.x = x
        self.y = y
        self.max_capacity = max_capacity
        self.color = color
        self.current_drones: list = []  # Nossa lista para controlar quem está nela

    @abstractmethod
    def get_cost(self) -> int:
        """Retorna o custo de entrada na zona."""
        pass


class NormalZone(Zone):
    def get_cost(self) -> int:

        return 1


class RestrictedZone(Zone):
    def get_cost(self) -> int:
        return 2