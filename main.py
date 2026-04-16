import sys
import pygame
from parse import parse_map
from simulation import Simulation
from algorithms.pathfinding import build_distance_map
from visualizer.vizu import Visualizador


def main() -> None:
    # 1. Verifica se o usuário passou o nome do mapa no terminal
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file.txt>")
        sys.exit(1)

    map_file = sys.argv[1]

    try:
        
        my_map, total_drones = parse_map(map_file)
        gps = build_distance_map(my_map)
        sim = Simulation(my_map, total_drones)
        
        # setup grafic
        pygame.init()
        viz = Visualizador()
        tela = pygame.display.set_mode((viz.largura, viz.altura))
        pygame.display.set_caption(f"Fly-in Simulation: {map_file}")
        relogio = pygame.time.Clock()
        
        historico_estados = []
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                
                if evento.type == pygame.KEYDOWN:
                    # AVANÇAR (Seta Direita)
                    if evento.key == pygame.K_RIGHT:
                        if not sim.is_finished():
                            now = []
                            for d in sim.drones:
                                # Guardamos EXATAMENTE 6 itens
                                estado = (
                                    d.id,               # 0
                                    d.current_zone,     # 1
                                    d.target_zone,      # 2
                                    d.arrival_turn,     # 3
                                    d.active_connection, # 4
                                    d.flight_cost       # 5
                                )
                                now.append(estado)
                            
                            # Guarda o turno atual e a lista de estados
                            historico_estados.append((sim.turn, now))
                            
                            # 2. Executa a lógica de movimento
                            sim.run_autopilot_turn(gps)

                    # VOLTAR (Seta Esquerda)
                    elif evento.key == pygame.K_LEFT:
                        if historico_estados:
                            # 1. Recupera o último estado salvo
                            turno_salvo, dados_recuperados = historico_estados.pop()
                            
                            # 2. Restaura o turno global
                            sim.turn = turno_salvo
                            
                            # 3. Restaura cada drone (Desempacota os 6 itens)
                            for i, drone in enumerate(sim.drones):
                                # A ordem aqui TEM que ser a mesma do Snapshot
                                d_id, cur, tar, arr, conn, cost = dados_recuperados[i]
                                
                                drone.id = d_id
                                drone.current_zone = cur
                                drone.target_zone = tar
                                drone.arrival_turn = arr
                                drone.active_connection = conn
                                drone.flight_cost = cost
                            
                            print(f"Retornando para o turno {sim.turn}")
            tela.fill((44, 62, 80))
            viz.draw_mapa(tela, my_map.zones, my_map.connections)
            viz.draw_drones(tela, sim.drones, sim.turn)
            
            txt_turno = viz.fonte.render(f"Turno Atual: {sim.turn}", True, (255, 255, 255))
            tela.blit(txt_turno, (20, 20))
            
            pygame.display.flip()
            relogio.tick(60)
        pygame.quit()

    except Exception as error:
            print(f"Error: {error}")
            sys.exit(1)

if __name__ == '__main__':
    main() 




"""         print(f"Map: {map_file} loaded. Total Drones: {total_drones}")
        
        
        # 5. O Loop Automático
        max_turns = 150 # Limite de segurança
        while not sim.is_finished() and sim.turn < max_turns:
            sim.run_autopilot_turn(gps)
            
            
        if sim.is_finished():
            print(f"\nSUCCESS! All drones arrived in {sim.turn} turns! 🎉")
        else:
            print(f"\nTIMEOUT! Simulation stopped after {max_turns} turns.")
            
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == '__main__':
    main() """