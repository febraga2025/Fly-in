import pygame
from typing import List, Tuple, Dict
from models.zone import Zone
from models.connections import Connection
from models.drone import Drone


class Visualizer:
    def __init__(self, width: int = 1600, height: int = 600) -> None:
        self.width = width
        self.height = height
        self.margin = 100
        # adjust according to map size
        self.scale = 70
        self.offset_x = 40   # Increase to push to the RIGHT
        self.offset_y = 250
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.colors_rgb = {
            "black": (44, 44, 44),
            "blue": (52, 152, 219),
            "brown": (120, 84, 62),
            "crimson": (192, 57, 43),
            "cyan": (26, 188, 156),
            "darkred": (139, 0, 0),
            "gold": (241, 196, 15),
            "green": (46, 204, 113),
            "lime": (46, 204, 113),
            "magenta": (155, 89, 182),
            "maroon": (128, 0, 0),
            "orange": (230, 126, 34),
            "purple": (142, 68, 173),
            "rainbow": (155, 89, 182),
            "yellow": (241, 196, 15),
            "red": (231, 76, 60),
            "violet": (142, 68, 173),
            "gray": (149, 165, 166),
            "grey": (149, 165, 166),
            "none": (189, 195, 199),
            "background": (44, 62, 80),
            "line": (127, 140, 141)
        }

    def screen_pos(self, x_map: int, y_map: int) -> Tuple[int, int]:
        """Convert map coordinates to screen pixels with manual adjustment."""
        x = (x_map * self.scale) + self.offset_x
        y = (y_map * self.scale) + self.offset_y
        return (int(x), int(y))

    def draw_map(self, screen: pygame.Surface, zones: Dict[str, Zone],
                 connections: List[Connection]) -> None:

        # draw connections first
        for conn in connections:
            p1 = self.screen_pos(conn.zone_a.x, conn.zone_a.y)
            p2 = self.screen_pos(conn.zone_b.x, conn.zone_b.y)
            pygame.draw.line(screen, self.colors_rgb["line"], p1, p2, 2)

        # draw zones (hubs)
        for zone in zones.values():
            pos = self.screen_pos(zone.x, zone.y)
            color_name = zone.color if zone.color else "none"
            color = self.colors_rgb.get(
                color_name.lower(), self.colors_rgb["none"]
            )

            if zone.__class__.__name__ == "RestrictedZone":
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = pos
                pygame.draw.rect(screen, color, rect)
            else:
                pygame.draw.circle(screen, color, pos, 20)

            txt = self.font.render(zone.name, True, (255, 255, 255))
            screen.blit(txt, (pos[0] - 20, pos[1] + 30))

    def draw_drones(
        self, screen: pygame.Surface, drones: List[Drone],
        turn_current: int
    ) -> None:
        for i, drone in enumerate(drones):
            # 1. If drone is flying (in transit)
            if (
                drone.target_zone and drone.current_zone is None and
                drone.active_connection is not None
            ):
                # Get the zone from which it came
                origin_obj = (
                    drone.active_connection.get_opposite_zone(
                        drone.target_zone
                    )
                )

                p_start = self.screen_pos(origin_obj.x, origin_obj.y)
                p_end = self.screen_pos(
                    drone.target_zone.x, drone.target_zone.y
                )

                # Calculate progress
                turns_remaining = drone.arrival_turn - turn_current

                if (
                    isinstance(drone.flight_cost, int) and
                    drone.flight_cost > 0
                ):
                    turns_passed = (
                        drone.flight_cost - turns_remaining + 1
                    )
                    ratio = turns_passed / drone.flight_cost
                    ratio = max(0.0, min(1.0, ratio))
                else:
                    ratio = 1.0

                # Linear Interpolation (LERP)
                pos_x = (
                    p_start[0] + (p_end[0] - p_start[0]) * ratio
                )
                pos_y = (
                    p_start[1] + (p_end[1] - p_start[1]) * ratio
                )
                pos = (int(pos_x), int(pos_y))

            # 2. If drone is stopped in a zone
            elif drone.current_zone:
                pos = self.screen_pos(
                    drone.current_zone.x, drone.current_zone.y
                )
            else:
                continue

            # 3. Visual drawing (offset to avoid overlap)
            pos_v = (pos[0] + (i % 5) * 4, pos[1] + (i // 5) * 4)
            pygame.draw.circle(screen, (0, 255, 255), pos_v, 10)
            pygame.draw.circle(screen, (255, 255, 255), pos_v, 10, 2)
            # Draw drone ID
            text = self.font.render(drone.id, True, (255, 255, 255))
            # Text follows the offset circle
            screen.blit(text, (pos_v[0] - 10, pos_v[1] - 25))
