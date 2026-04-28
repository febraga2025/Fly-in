# Exemplos Práticos e Diagramas

## 1. EXAMPLE: LINEAR PATH

### Mapa
```
nb_drones: 2
start_hub: hub 0 0
end_hub: goal 3 0
hub: waypoint1 1 0
hub: waypoint2 2 0
connection: hub-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Grafo Visual
```
[hub] --1-- [waypoint1] --1-- [waypoint2] --1-- [goal]
 D1,D2      empty              empty              ∅
```

### GPS Map (Reverse Dijkstra)
```
goal = 0
waypoint2 = 1 (cost 1)
waypoint1 = 2 (cost 1)
hub = 3 (cost 1)
```

### Simulação

```
TURNO 1:
Estado antes: D1,D2 em hub
Decisão:
  - D1: vizinhos=[waypoint1]
    - waypoint1: occupancy=0, distance=2, virtual=2 ✓
    - D1 escolhe waypoint1
  - D2: vizinhos=[waypoint1]
    - waypoint1: occupancy=1 (D1 vai lá), max=1
    - D2 não pode (zona cheia), fica
Output: D1-waypoint1
Estado depois: D1 em voo, D2 em hub

TURNO 2:
Estado antes: D1 chega waypoint1, D2 em hub
Decisão:
  - D1: em waypoint1, vizinhos=[hub, waypoint2]
    - hub: distance=3 (volta, rejeitado)
    - waypoint2: distance=1 ✓
    - D1 escolhe waypoint2
  - D2: em hub, vizinhos=[waypoint1]
    - waypoint1: occupancy=0 (D1 saiu), distance=2 ✓
    - D2 escolhe waypoint1
Output: D1-waypoint2 D2-waypoint1
Estado depois: D1 em voo, D2 em voo

TURNO 3:
Estado antes: D1 chega waypoint2, D2 chega waypoint1
Decisão:
  - D1: em waypoint2, vizinhos=[waypoint1, goal]
    - waypoint1: distance=2 (volta, rejeitado)
    - goal: distance=0 ✓
    - D1 escolhe goal
  - D2: em waypoint1, vizinhos=[hub, waypoint2]
    - hub: distance=3 (volta, rejeitado)
    - waypoint2: distance=1 ✓
    - D2 escolhe waypoint2
Output: D1-goal D2-waypoint2
Estado depois: D1 terminado! ✓, D2 em voo

TURNO 4:
Estado antes: D2 chega waypoint2
Decisão:
  - D2: em waypoint2, vizinhos=[waypoint1, goal]
    - waypoint1: distance=2 (volta, rejeitado)
    - goal: distance=0 ✓
    - D2 escolhe goal
Output: D2-goal
Estado depois: D2 terminado! ✓

TOTAL: 4 turnos
```

---

## 2. EXAMPLE: PRIORITY ZONE

### Mapa
```
nb_drones: 2
start_hub: hub 0 0
end_hub: goal 2 0
hub: normal_zone 1 -1 [zone=normal]
hub: priority_zone 1 1 [zone=priority]
connection: hub-normal_zone
connection: hub-priority_zone
connection: normal_zone-goal
connection: priority_zone-goal
```

### Grafo Visual
```
              [priority_zone]
                    |
[hub] ----------+----------  [goal]
   D1,D2        |
         [normal_zone]
```

### GPS Map
```
goal = 0
normal_zone = 1 (cost 1)
priority_zone = 1 (cost 1)
hub = 2 (cost 1)
```

### Simulação

```
TURNO 1:
Decisão D1:
  - normal_zone: distance=1, virtual=1.0
  - priority_zone: distance=1, virtual=0.9 ← VENCE (prioridade!)
  D1 vai para priority_zone
Decisão D2:
  - normal_zone: distance=1, virtual=1.0 ← ESCOLHE (priority ocupada)
  D2 vai para normal_zone
Output: D1-priority_zone D2-normal_zone

TURNO 2:
Decisão D1:
  - goal: distance=0 ✓
  D1 vai para goal
Decisão D2:
  - goal: distance=0 ✓
  D2 vai para goal
Output: D1-goal D2-goal

TOTAL: 2 turnos (bem otimizado!)
```

---

## 3. EXAMPLE: RESTRICTED ZONE

### Mapa
```
nb_drones: 1
start_hub: hub 0 0
end_hub: goal 2 0
hub: restricted_zone 1 0 [zone=restricted]
connection: hub-restricted_zone
connection: restricted_zone-goal
```

### Grafo Visual
```
[hub] --1-- [restricted_zone] --2-- [goal]
 D1         (takes 2 turns!)
```

### GPS Map
```
goal = 0
restricted_zone = 2 (cost 2!)
hub = 4 (cost 2)
```

### Simulação

```
TURNO 1:
Estado: D1 em hub
Decisão:
  - restricted_zone: distance=2
    D1 vai para restricted_zone (custa 2 turnos!)
    Mudança: current_zone = None, target_zone = restricted_zone
             arrival_turn = 1 + 2 = 3
             active_connection = hub-restricted_zone
Output: D1-restricted_zone

TURNO 2:
Estado: D1 está voando (arrival_turn = 3 > current_turn = 2)
- D1 NÃO está em nenhuma zona
- D1 NÃO pode se mover (is_flying = True)
- Nada acontece
Output: (nada)

TURNO 3:
Estado: D1 chega (arrival_turn = 3 == current_turn = 3)
Landing phase: current_zone = target_zone = restricted_zone
               target_zone = None
Decisão:
  - goal: distance=0
    D1 vai para goal
Output: D1-goal

TOTAL: 3 turnos
```

---

## 4. EXAMPLE: CAPACITY CONFLICT

### Mapa
```
nb_drones: 2
start_hub: hub 0 0 [max_drones=2]
end_hub: goal 2 0 [max_drones=2]
hub: bottleneck 1 0 [max_drones=1]  ← SÓ 1 DRONE!
connection: hub-bottleneck [max_link_capacity=1]  ← SÓ 1!
connection: bottleneck-goal
```

### Grafo Visual
```
[hub] ==1== [bottleneck] --- [goal]
 D1,D2     (capacity: 1!)   D1,D2
```

### Simulação

```
TURNO 1:
Estado: D1,D2 em hub
Decisão D1:
  - bottleneck: occupancy=0 < max_drones=1 ✓
                connection A-B usage=0 < capacity=1 ✓
    D1 pode ir
Decisão D2:
  - bottleneck: occupancy=1 (D1 vai lá) == max_drones=1
    D2 não pode (zona vai ficar cheia!)
    D2 fica em hub
Output: D1-bottleneck
Estado: D1 em bottleneck, D2 em hub

TURNO 2:
Estado: D1 em bottleneck, D2 em hub
Decisão D1:
  - goal: distance=0 ✓
    D1 pode ir
Decisão D2:
  - bottleneck: occupancy=0 (D1 saiu) < max_drones=1 ✓
                connection usage=0 < capacity=1 ✓
    D2 pode ir
Output: D1-goal D2-bottleneck
Estado: D1 terminado! D2 em bottleneck

TURNO 3:
Decisão D2:
  - goal: distance=0 ✓
    D2 vai para goal
Output: D2-goal
Estado: D2 terminado!

TOTAL: 3 turnos
```

---

## 5. DIAGRAM: RUN_AUTOPILOT_TURN FLOW

```
┌─────────────────────────────────────┐
│  START: run_autopilot_turn(gps)     │
│  Turn N → Turn N+1                  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  PHASE 1: LANDING                   │
│  Para cada drone:                   │
│  if turn >= arrival_turn:           │
│    current_zone = target_zone       │
│    target_zone = None               │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  PHASE 2: ARRIVAL RADAR             │
│  (Aviso para restricted zones)      │
│  if turn == (arrival_turn - 1):     │
│    print(f"{drone.id}-{zone.name}") │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  PHASE 3: CONNECTION CENSUS         │
│  conn_usage: Dict[Connection, int]  │
│  Para cada drone voando:            │
│    conn_usage[conn] += 1            │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  PHASE 4: FILTER MOVABLE DRONES     │
│  drones_to_move = [d for d in       │
│    drones if                        │
│    not d.is_flying(turn) and        │
│    d.current_zone != end_zone]      │
└─────────────────────────────────────┘
                ↓
┌──────────────────────────────────────────┐
│  PHASE 5: DECIDE ROUTES (O ALGORITMO!)   │
│  Para cada drone em drones_to_move:      │
│                                          │
│    best_neighbor = None                  │
│    best_dist = 999999                    │
│                                          │
│    Para cada conexão:                    │
│      if drone.current_zone in conn:      │
│        neighbor = opposite_zone          │
│                                          │
│        if neighbor.can_enter() and       │
│           occupancy(neighbor)            │
│           < neighbor.max_drones:         │
│                                          │
│          if conn_usage[conn]             │
│             < conn.max_capacity:         │
│                                          │
│            dist = gps[neighbor]          │
│            if priority: dist -= 0.1      │
│                                          │
│            if dist <= current_dist       │
│               and dist < best_dist:      │
│              best_neighbor = neighbor    │
│              best_dist = dist            │
│              best_conn = conn            │
│                                          │
│    if best_neighbor:                     │
│      drone.target_zone = best_neighbor   │
│      drone.arrival_turn = turn + cost    │
│      drone.active_connection = best_conn │
│      drone.current_zone = None           │
│      output.append(f"move")              │
│                                          │
│    else:                                 │
│      output omits this drone             │
└──────────────────────────────────────────┘
                ↓
┌──────────────────────────────────────────┐
│  PHASE 6: APPLY MOVEMENTS & OUTPUT       │
│  print(" ".join(turn_outputs))           │
└──────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  END: Próximo turno                 │
└─────────────────────────────────────┘
```

---

## 6. DIAGRAM: GREEDY DECISION TREE

```
Para cada vizinho possível:

┌─ Tem espaço na zona?
│  ├─ NÃO → skip
│  └─ SIM ↓
│
├─ Tem espaço na conexão?
│  ├─ NÃO → skip
│  └─ SIM ↓
│
├─ Calcula distância
│  ├─ Priority? dist - 0.1
│  └─ Normal? dist
│
├─ Nunca volta para trás?
│  ├─ NÃO (dist > current_dist) → skip
│  └─ SIM ↓
│
└─ É o melhor até agora?
   ├─ SIM → salva como best_neighbor
   └─ NÃO → continua
```

---

## 7. STATE TRANSITIONS

### Drone State Machine

```
┌─────────────────┐
│  START          │
│ current_zone=A  │
│ target_zone=∅   │
└────────┬────────┘
         │
         │ Decide to move to B
         ↓
┌─────────────────┐
│  IN_FLIGHT      │  (Multi-turn movement)
│ current_zone=∅  │
│ target_zone=B   │
│ arrival_turn=N  │
└────────┬────────┘
         │
         │ arrival_turn == current_turn
         ↓
┌─────────────────┐
│  ARRIVED        │
│ current_zone=B  │
│ target_zone=∅   │
└─────────────────┘
```

---

## 8. PERFORMANCE METRICS

### Linear Path (2 drones)
```
Theoretical minimum: 1 + 1 + 1 = 3 turns (if perfect)
Actual: 4 turns
Target: ≤ 6 turns ✓
```

### Simple Fork (3 drones)
```
Theoretical: N + M turns (N = longest path)
Actual: 6 turns
Target: ≤ 6 turns ✓
```

### Bottleneck Pattern (2 drones, 1 capacity)
```
Time = D * (path_length)
3 drones, bottleneck = 3 * 3 = 9 turns
```

---

## 9. QUICK REFERENCE: ZONE TYPES

| Tipo | Custo | Vantagem | Desvantagem |
|------|-------|----------|------------|
| Normal | 1 | Rápido | Nenhum |
| Priority | 1 | Preferencial | Nenhum |
| Restricted | 2 | Forçar espera | Lento |
| Blocked | ∞ | Bloqueia | Inacessível |

---

**Pronto para explicar! 🎯**
