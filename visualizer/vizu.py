import pygame
from typing import List, Tuple, Dict
from models.zone import Zone
from models.connections import Connection
from models.drone import Drone


class Visualizador:
    def __init__(self, largura: int = 1900, altura: int = 800) -> None: 
        self.largura = largura
        self.altura = altura
        self.margem = 100
        # ajusta de acordo com tamanho do mapa
        self.escala = 70
        self.desloc_x = 150   # Aumente para empurrar para a DIREITA
        self.desloc_y = 250
        pygame.font.init()
        self.fonte = pygame.font.SysFont("Arial", 14, bold=True)
        self.cores_rgb = {
            "green": (46, 204, 113),
            "yellow": (241, 196, 15),
            "red": (231, 76, 60),
            "gray": (149, 165, 166),
            "none": (189, 195, 199),
            "fundo": (44, 62, 80),
            "linha": (127, 140, 141)
        }

    def p_tela(self, x_mapa: int, y_mapa: int) -> Tuple[int, int]:
        """Converte coordenadas do mapa para pixels com ajuste manual."""
        # Multiplicamos pela escala e somamos o deslocamento manual
        x = (x_mapa * self.escala) + self.desloc_x
        y = (y_mapa * self.escala) + self.desloc_y
        return (int(x), int(y))

    def draw_mapa(self, tela: pygame.Surface, zones: Dict[str, Zone],
                  connections: List[Connection]) -> None:
        
        # draw conex first
        for conn in connections:
            p1 = self.p_tela(conn.zone_a.x, conn.zone_a.y)
            p2 = self.p_tela(conn.zone_b.x, conn.zone_b.y)
            pygame.draw.line(tela, self.cores_rgb["linha"], p1, p2, 2)

        # draw zone(hub)
        for zone in zones.values():
            pos = self.p_tela(zone.x, zone.y)
            cor_nome = zone.color if zone.color else "none"
            cor = self.cores_rgb.get(cor_nome.lower(), self.cores_rgb["none"])

            if zone.__class__.__name__ == "RestrictedZone":
                rect = pygame.Rect(0, 0, 40, 40)
                rect.center = pos
                pygame.draw.rect(tela, cor, rect)
            else:
                pygame.draw.circle(tela, cor, pos, 20)

            txt = self.fonte.render(zone.name, True, (255, 255, 255))
            tela.blit(txt, (pos[0] - 20, pos[1] + 30))
        
    def draw_drones(self, tela: pygame.Surface, drones: List[Drone], turno_atual: int) -> None:
        for i, drone in enumerate(drones):
            # 1. Se o drone está voando (em trânsito)
            if drone.target_zone and drone.current_zone is None:
                # Pegamos a zona de onde ele veio
                origem_obj = drone.active_connection.get_opposite_zone(drone.target_zone)
                
                p_start = self.p_tela(origem_obj.x, origem_obj.y)
                p_end = self.p_tela(drone.target_zone.x, drone.target_zone.y)

                # Cálculo do progresso
                turnos_restantes = drone.arrival_turn - turno_atual

                if (
                    isinstance(drone.flight_cost, int)
                    and drone.flight_cost > 0
                ):
                    turnos_passados = drone.flight_cost - turnos_restantes + 1
                    ratio = turnos_passados / drone.flight_cost
                    ratio = max(0.0, min(1.0, ratio))
                else:
                    ratio = 1.0
                
                # Interpolação Linear (LERP)
                pos_x = p_start[0] + (p_end[0] - p_start[0]) * ratio
                pos_y = p_start[1] + (p_end[1] - p_start[1]) * ratio
                pos = (int(pos_x), int(pos_y))

            # 2. Se o drone está parado em uma zona
            elif drone.current_zone:
                pos = self.p_tela(drone.current_zone.x, drone.current_zone.y)
            else:
                continue

            # 3. Desenho visual (offset para não embolar)
            pos_v = (pos[0] + (i % 5) * 4, pos[1] + (i // 5) * 4)
            pygame.draw.circle(tela, (0, 255, 255), pos_v, 10)
            pygame.draw.circle(tela, (255, 255, 255), pos_v, 10, 2)
            # Desenha o ID do drone
            texto = self.fonte.render(drone.id, True, (255, 255, 255))
            # Texto acompanha o círculo deslocado
            tela.blit(texto, (pos_v[0] - 10, pos_v[1] - 25))
