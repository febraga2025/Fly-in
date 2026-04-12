import re
from typing import Dict, Tuple

from models.zone import (
    Zone,
    NormalZone,
    RestrictedZone,
    PriorityZone,
    BlockedZone
)
from models.connections import Connection
from models.graph import MapGraph


def extract_metadata(line: str) -> Tuple[str, Dict[str, str]]:
    metadata = {}
    match = re.search(r'\[(.*?)\]', line)  # re procura qualquer coisa entre
    # colchetes

    if match:
        content = match.group(1)
        pairs = content.split()

        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                metadata[key] = value

        line = line[:match.start()].strip()
    return line, metadata


def create_zone_object(name, x: int, y: int, metadata: Dict[str, str],
                       is_start: bool, is_end: bool) -> Zone:
    """
    Essa é uma "Factory Function" (Fábrica). Ela decide qual classe filha de 
    Zone
    ela deve instanciar baseada no metadado 'zone'.
    """
    z_type = metadata.get('zone', 'normal')
    max_drones = int(metadata.get('max_drones', 1))
    color = metadata.get('color', None)
    max_drones = int(metadata.get('max_drones', 1))
    if max_drones <= 0:
        raise ValueError("max_drones must be strictly positive.")
    
    if z_type == 'normal':
        zone = NormalZone(name, x, y, max_drones, color)
    elif z_type == 'restricted':
        zone = RestrictedZone(name, x, y, max_drones, color)
    elif z_type == 'priority':
        zone = PriorityZone(name, x, y, max_drones, color)
    elif z_type == 'blocked':
        zone = BlockedZone(name, x, y, max_drones, color)
    else:
        raise ValueError(f"Invalid zone type: {z_type}")

    zone.is_start = is_start
    zone.is_end = is_end

    if is_start or is_end:
        zone.max_drones = 999999
    return zone


def parse_map(file_path: str) -> Tuple[MapGraph, int]:
    """
    Lê o arquivo TXT, linha por linha, e constrói o mapa.
    Retorna o MapGraph populado e a quantidade total de drones.
    """
    map_graph = MapGraph()  # Mudei de 'map' para 'map_graph' para não dar erro
    nb_drones = 0
    has_start = False
    has_end = False
    
    is_first_line = True               # Flag para saber se estamos na 1ª linha
    seen_connections = set()           # Memória para não deixar duplicar conexões

    with open(file_path, 'r') as f:
        for line_num, original_line in enumerate(f, start=1):
            line = original_line.strip()

            if not line or line.startswith('#'):
                continue
            
            try:
                # --- REGRA 1: Primeira linha obrigatoriamente é nb_drones ---
                if is_first_line:
                    if not line.startswith('nb_drones:'):
                        raise ValueError("The first line must define nb_drones.")
                    
                    nb_drones = int(line.split(':')[1].strip())
                    if nb_drones <= 0:
                        raise ValueError("The number of drones should be positive.")
                    is_first_line = False
                    continue

                # --- REGRA 2: Zonas ---
                elif any(line.startswith(prefix) for prefix in ['start_hub:', 'end_hub:', 'hub:']):
                    clean_line, metadata = extract_metadata(line)
                    prefix, data = clean_line.split(':', 1)
                    parts = data.strip().split()

                    if len(parts) != 3:
                        raise ValueError("Invalid zone format. Expected: name x y")
                    
                    is_start = prefix == 'start_hub'
                    is_end = prefix == 'end_hub'

                    # Bloqueia se tentar colocar dois Starts ou dois Ends
                    if is_start:
                        if has_start:
                            raise ValueError("Multiple start_hubs found.")
                        has_start = True
                        
                    if is_end:
                        if has_end:
                            raise ValueError("Multiple end_hubs found.")
                        has_end = True

                    name = parts[0]
                    x = int(parts[1])
                    y = int(parts[2])

                    if '-' in name:
                        raise ValueError(f"Zone name cannot contain dashes: {name}")

                    new_zone = create_zone_object(name, x, y, metadata, is_start, is_end)
                    map_graph.add_zone(new_zone)

                # --- REGRA 3: Conexões ---
                elif line.startswith('connection:'):
                    clean_line, metadata = extract_metadata(line)
                    data = clean_line.split(':')[1].strip()

                    z1_name, z2_name = data.split('-')
                    
                    # Bloqueia conexões duplicadas (ex: a-b e b-a)
                    conn_id1 = f"{z1_name}-{z2_name}"
                    conn_id2 = f"{z2_name}-{z1_name}"
                    if conn_id1 in seen_connections or conn_id2 in seen_connections:
                        raise ValueError(f"Duplicate connection: {conn_id1}")
                    
                    # Adiciona na memória
                    seen_connections.add(conn_id1)
                    seen_connections.add(conn_id2)

                    z1 = map_graph.get_zone(z1_name)
                    z2 = map_graph.get_zone(z2_name)

                    cap = int(metadata.get('max_link_capacity', 1))
                    
                    # Bloqueia conexões com capacidade 0
                    if cap <= 0:
                        raise ValueError("Connection capacity must be strictly positive.")

                    new_connection = Connection(z1, z2, cap)
                    map_graph.add_connection(new_connection)

                else:
                    raise ValueError(f"Unrecognized command: {line.split(':')[0]}")
                    
            except Exception as e:
                raise Exception(f"Parse error on line {line_num}: {e}")

        # Validação final pós-leitura
        if not has_start or not has_end:
            raise ValueError("The map must contain exactly one 'start_hub' and one 'end_hub'.")
            
        return map_graph, nb_drones