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
    # regex searches for anything between brackets
    match = re.search(r'\[(.*?)\]', line)

    if match:
        content = match.group(1)
        pairs = content.split()

        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                metadata[key] = value

        line = line[:match.start()].strip()
    return line, metadata


def create_zone_object(name: str, x: int, y: int,
                       metadata: Dict[str, str],
                       is_start: bool, is_end: bool) -> Zone:
    """
    This is a "Factory Function". It decides which subclass of Zone
    should be instantiated based on the 'zone' metadata.
    """
    z_type = metadata.get('zone', 'normal')
    max_drones = int(metadata.get('max_drones', 1))
    color = metadata.get('color', None)
    max_drones = int(metadata.get('max_drones', 1))
    if max_drones <= 0:
        raise ValueError("max_drones must be strictly positive.")

    zone: Zone
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
    Reads the TXT file, line by line, and builds the map.
    Returns the populated MapGraph and the total number of drones.
    """
    map_graph = MapGraph()
    nb_drones = 0
    has_start = False
    has_end = False

    is_first_line = True
    seen_connections = set()

    with open(file_path, 'r') as f:
        for line_num, original_line in enumerate(f, start=1):
            line = original_line.strip()

            if not line or line.startswith('#'):
                continue

            try:
                # --- RULE 1: First line must be nb_drones ---
                if is_first_line:
                    if not line.startswith('nb_drones:'):
                        msg = "The first line must define nb_drones."
                        raise ValueError(msg)

                    nb_drones = int(line.split(':')[1].strip())
                    if nb_drones <= 0:
                        msg = "The number of drones should be positive."
                        raise ValueError(msg)
                    is_first_line = False
                    continue

                # --- RULE 2: Zones ---
                elif any(
                    line.startswith(prefix)
                    for prefix in ['start_hub:', 'end_hub:', 'hub:']
                ):
                    clean_line, metadata = extract_metadata(line)
                    prefix, data = clean_line.split(':', 1)
                    parts = data.strip().split()

                    if len(parts) != 3:
                        msg = (
                            "Invalid zone format. "
                            "Expected: name x y"
                        )
                        raise ValueError(msg)

                    is_start = prefix == 'start_hub'
                    is_end = prefix == 'end_hub'

                    # Block if trying to add multiple starts or ends
                    if is_start:
                        if has_start:
                            raise ValueError(
                                "Multiple start_hubs found."
                            )
                        has_start = True

                    if is_end:
                        if has_end:
                            raise ValueError("Multiple end_hubs found.")
                        has_end = True

                    name = parts[0]
                    x = int(parts[1])
                    y = int(parts[2])

                    if '-' in name:
                        msg = (
                            f"Zone name cannot contain dashes: {name}"
                        )
                        raise ValueError(msg)

                    new_zone = create_zone_object(
                        name, x, y, metadata, is_start, is_end
                    )
                    map_graph.add_zone(new_zone)

                # --- RULE 3: Connections ---
                elif line.startswith('connection:'):
                    clean_line, metadata = extract_metadata(line)
                    data = clean_line.split(':')[1].strip()

                    z1_name, z2_name = data.split('-')

                    # Block duplicate connections
                    conn_id1 = f"{z1_name}-{z2_name}"
                    conn_id2 = f"{z2_name}-{z1_name}"
                    if (
                        conn_id1 in seen_connections or
                        conn_id2 in seen_connections
                    ):
                        raise ValueError(
                            f"Duplicate connection: {conn_id1}"
                        )

                    # Add to memory
                    seen_connections.add(conn_id1)
                    seen_connections.add(conn_id2)

                    z1 = map_graph.get_zone(z1_name)
                    z2 = map_graph.get_zone(z2_name)

                    cap = int(metadata.get('max_link_capacity', 1))

                    # Block connections with 0 capacity
                    if cap <= 0:
                        msg = (
                            "Connection capacity "
                            "must be strictly positive."
                        )
                        raise ValueError(msg)

                    new_connection = Connection(z1, z2, cap)
                    map_graph.add_connection(new_connection)

                else:
                    cmd = line.split(':')[0]
                    raise ValueError(f"Unrecognized command: {cmd}")

            except Exception as e:
                raise Exception(f"Parse error on line {line_num}: {e}")

        # Final validation after reading
        if not has_start or not has_end:
            msg = (
                "The map must contain exactly one "
                "'start_hub' and one 'end_hub'."
            )
            raise ValueError(msg)

        return map_graph, nb_drones
