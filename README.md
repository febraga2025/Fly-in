*This project has been created as part of the 42 curriculum by febraga.*

# Fly-in: Autonomous Drone Routing

## Description
Fly-in is an autonomous drone routing simulator. The project's goal is to manage the traffic of a drone fleet across a network of zones (a graph), from a starting point to a final destination. The system ensures that drones always choose the shortest and fastest path while strictly respecting the capacity limits of each zone and connection, preventing collisions and traffic jams along the way.

## Instructions
The project includes a `Makefile` to automate all tasks. 

**Installation:**
To set up the virtual environment and install Pygame:
`make install`

**Execution:**
To run the simulation in the strict/evaluation mode (text only):
`make run MAP=maps/easy/01_linear_path.txt`
*(Or run manually: `python3 main.py <map_file.txt>`)*

To run the simulation with the graphical interface:
`python3 main.py maps/easy/01_linear_path.txt --visual`

**Code Quality & Cleaning:**
`make lint` (Checks static typing with Mypy and formatting with Flake8)
`make clean` (Removes caches and virtual environments)

## Algorithm & Strategy
The simulation's "brain" acts as a smart navigation system. First, we use a **Reverse Dijkstra** algorithm starting from the end zone to create a global "GPS map" of optimal distances. 

During each turn, every drone's autopilot evaluates its neighboring zones using a greedy approach: it checks if the target zone and the connection have available capacity (making sure no one is in the way), and then chooses the shortest path available, always favoring priority zones when possible.

## Visual Representation
The graphical interface was built using the `pygame` library. The simulation engine saves a state history (a snapshot dictionary) of each turn to allow visual replay. The window dynamically renders the map, plotting the zones, connections, and metadata colors exactly as defined in the input text file. It displays the exact position of each drone in real-time as they move across the nodes.

## Resources & AI Usage
**Resources:**
* Pathfinding algorithms study: Wikipedia and Red Blob Games tutorials on Dijkstra.
* Pygame official documentation for rendering and event handling.
* Python `typing` documentation for strict Mypy compliance.

**AI Usage:**
Artificial Intelligence (LLMs) was used as a support tool during the project, specifically to brainstorm and improve logical reasoning for the algorithm structure, to help find and interpret documentation (such as static typing errors and Pygame behaviors), and to review code formatting to ensure strict compliance with the Flake8 standards.

## Project Structure

    .
    ├── main.py                 # Entry point
    ├── parse.py               # Map file parser
    ├── simulation.py          # Simulation engine
    ├── simulation_runner.py    # Simulation orchestrator
    ├── algorithms/
    │   └── pathfinding.py    # Dijkstra implementation
    ├── models/
    │   ├── zone.py           # Zone class hierarchy
    │   ├── drone.py          # Drone class
    │   ├── graph.py          # MapGraph class
    │   └── connections.py    # Connection class
    ├── visualizer/
    │   ├── vizu.py          # Pygame visualization
    │   └── replay.py        # Replay system
    ├── maps/                  # Test maps
    ├── Makefile              # Build automation
    └── README.md             # This file

**Created by**: febraga  
**Language**: Python 3.10+  
**License**: 42 Curriculum Project