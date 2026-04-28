# Script de Apresentação - 5 Minutos

## VERSION 1: SUPER RÁPIDO (2 MIN)

---

**Olá! Meu projeto é Fly-in: um simulador de roteamento de drones autônomos.**

**Problema**: Mover N drones de um ponto de partida para um destino no **menor tempo possível**.

**Solução**:
1. **Pathfinding**: Reverse Dijkstra calcula distância de cada zona até o destino (uma vez no início)
2. **Simulação**: Cada turno, cada drone escolhe o melhor vizinho usando greedy:
   - Respeita capacidade de zonas e conexões
   - Nunca anda para trás
   - Prefere priority zones

**Características**:
- 4 tipos de zona: normal (1 turn), restricted (2 turns), priority (1 turn), blocked (✗)
- Type safe 100% (mypy ✓, flake8 ✓)
- OOP puro, sem bibliotecas externas
- Visual em tempo real com Pygame

**Resultados**: Easy maps dentro do target! ✓

---

## VERSION 2: MÉDIO (5 MIN)

---

**Olá! Meu projeto é Fly-in.**

**O Problema**:
Temos uma rede de zonas conectadas. N drones começam no start_hub e precisam chegar no end_hub. Cada zona tem limite de quantos drones podem estar lá. Cada conexão tem limite de quantos drones podem voar simultaneamente. Objetivo: fazer isso no menor número de turnos.

**A Solução tem 2 partes**:

**PARTE 1: Pathfinding (Preparação)**
- Usamos Reverse Dijkstra
- Começa no end_hub com distância 0
- Propaga para trás até start_hub
- Resultado: GPS map mostrando distância de cada zona até o destino
- Roda uma única vez no início

**PARTE 2: Simulação (Turn by Turn)**
- Cada turno:
  1. Drones que completaram viagem multi-turno pousam
  2. Contamos quantos drones estão voando em cada conexão
  3. Para cada drone que pode se mover:
     - Olha os vizinhos
     - Respeita capacidade (se tem espaço na zona? na conexão?)
     - Nunca anda para trás (só zonas com distância <= current_distance)
     - Prefere priority zones (desconto de 0.1 na distância)
     - Escolhe o melhor
  4. Todos os movimentos acontecem simultaneamente
- Repete até todos os drones chegarem

**Por que funciona?**
- GPS map garante que sempre há um caminho
- Greedy local ≈ ótimo global
- Capacidade é checada antes, então evitamos conflitos
- É rápido: O(D × C) por turno

**Tipos de Zona**:
- Normal: 1 turno
- Restricted: 2 turnos (drone fica voando 2 turnos)
- Priority: 1 turno, preferido no pathfinding
- Blocked: impossível entrar

**Estrutura do Código**:
- Parser: lê arquivo de mapa
- Models: Zone, Drone, Connection, MapGraph
- Pathfinding: Reverse Dijkstra
- Simulation: O coração, run_autopilot_turn()
- Visualizer: Pygame em tempo real

**Qualidade**:
- 100% type hints (mypy ✓)
- Flake8 completo
- OOP puro
- Sem bibliotecas externas (custom graph)

**Resultados**:
- Easy maps dentro do target
- Testes: Linear Path (4 turns, target 6), Simple Fork (6 turns, target 6)

---

## VERSION 3: COMPLETO (10 MIN)

---

**Problema**:

Temos uma rede de zonas (hubs) conectadas por estradas (connections). Cada zona pode ter múltiplos drones, mas tem um limite `max_drones`. Cada estrada tem um limite `max_link_capacity`. Drones começam todos no `start_hub` e precisam chegar no `end_hub`. O objetivo é fazer isso no menor número de turnos.

Zonas diferentes têm custos diferentes:
- Normal: 1 turno
- Restricted: 2 turnos (precisa planejar, drone fica em voo 2 turnos)
- Priority: 1 turno (preferido)
- Blocked: impossível

**Solução**:

**STEP 1: SETUP - Reverse Dijkstra (Pathfinding)**

Por que Reverse Dijkstra?
- Começamos no END (end_hub = distância 0)
- Propagamos para TRÁS até START
- Resultado: cada zona sabe sua distância até o destino
- Roda UMA VEZ no início
- Todos os drones usam esse GPS map toda a simulação
- Alternativa (forward Dijkstra) seria muito mais lenta

**STEP 2: SIMULATION - Turn by Turn**

Cada turno:

a) **LANDING PHASE**
   - Drones que completaram movimento multi-turno chegam na zona
   - Mudam de estado: target_zone → current_zone

b) **CENSUS**
   - Contamos quantos drones estão voando em cada conexão
   - Isso nos ajuda a respeitar max_link_capacity

c) **FILTER**
   - Selecionamos drones que podem se mover:
     * Não estão voando atualmente
     * Não estão no destino final

d) **DECIDE ROUTES** ← O ALGORITMO INTELIGENTE
   
   Para cada drone:
   ```
   Para cada vizinho:
     - Tem espaço na zona? NÃO → skip
     - Tem espaço na conexão? NÃO → skip
     - Calcula virtual_distance:
       * Se PriorityZone: distance - 0.1
       * Senão: distance
     - Nunca volta: distance <= current_distance?
     - Escolhe o com menor virtual_distance
   ```
   
   Por que isso funciona?
   - GPS map garante que sempre há progresso
   - Localmente ótimo ≈ globalmente ótimo
   - Simples e rápido
   - Evita deadlocks (capacidade checada antes)

e) **APPLY MOVEMENTS**
   - Todos os movimentos acontecem simultaneamente
   - Atualiza ocupação de conexões

**Repetir até todos chegarem**

**Multi-turn Movements**:

Quando drone vai para Restricted Zone (2 turnos):
- Turno N: drone deixa current_zone, entra em voo
  - `current_zone = None`
  - `target_zone = restrictedZone`
  - `arrival_turn = N + 2`
  - `active_connection = conn`
- Turno N+1: drone ainda voando
  - Ocupa a conexão
  - Não pode ser interrompido
- Turno N+2: drone chega
  - `current_zone = restrictedZone`
  - `target_zone = None`

**Conflitos e Capacidade**:

**Problema**: O que fazemos se dois drones querem a mesma zona?

**Solução**:
- Checamos `occupancy(zone) < zone.max_drones` ANTES de autorizar
- Se não tem espaço, drone fica onde está
- Próximo turno, tenta de novo

**Problema**: E conexões?

**Solução**:
- Mantemos `conn_usage: Dict[Connection, int]`
- Cada drone que sai ocupa uma "vaga"
- Se `conn_usage[conn] >= conn.max_link_capacity`, não sai
- Quando chega no destino, libera a vaga

**Exemplo Prático**:

```
2 drones, caminho: A → B → C
A-B capacity 1, B-C capacity 1

Turno 1:
- D1 quer ir A→B: sim (espaço em B, espaço em A-B)
- D2 quer ir A→B: não (A-B já tem D1)
Output: D1-B

Turno 2:
- D1 em B, quer ir B→C: sim
- D2 em A, quer ir A→B: sim (A-B agora livre)
Output: D1-C D2-B

Turno 3:
- D1 chega C: fim!
- D2 em B, quer ir B→C: sim
Output: D2-C
```

**Estrutura de Código**:

```
main.py
  └─ usa simulation_runner.py

simulation_runner.py
  ├─ chama parse.py → MapGraph
  ├─ chama pathfinding.py → GPS map
  ├─ cria Simulation
  └─ roda loop até finished()

simulation.py (O Coração)
  └─ run_autopilot_turn()
      ├─ landing phase
      ├─ radar
      ├─ census
      ├─ filter
      ├─ decide routes ← ALGORITMO
      └─ apply movements

models/
  ├─ zone.py: Zone (abstract) → Normal, Restricted, Priority, Blocked
  ├─ drone.py: Drone (id, current_zone, target_zone, ...)
  ├─ graph.py: MapGraph (zones dict, connections list, start/end)
  └─ connections.py: Connection (zone_a, zone_b, max_link_capacity)

visualizer/
  ├─ vizu.py: classe Visualizer (Pygame)
  └─ replay.py: interface interativa
```

**Type Safety**:

```python
def run_autopilot_turn(self, gps: Dict[str, int]) -> None:
    conn_usage: Dict[Connection, int] = {}
    best_conn: Connection | None = None
    ...
```

- Cada variável tem tipo
- Cada função tem tipos de entrada e saída
- Mypy: `mypy . --ignore-missing-imports` ✓ PASSED
- Flake8: `flake8 --exclude=.venv .` ✓ PASSED
- 14 arquivos, 0 erros

**Resultados**:

Easy maps:
- Linear Path (2 drones): 4 turns (target: 6) ✓
- Simple Fork (3 drones): 6 turns (target: 6) ✓
- Basic Capacity: em andamento

Complexidade:
- Setup: O(Z + C) uma vez
- Por turno: O(D × C)
- Espaço: O(Z + C + D)
- Na prática: muito rápido

---

## RESPOSTAS PRONTAS

### "Como evita deadlock?"
> "Verifica capacidade ANTES de autorizar movimento. Se a conexão está cheia, o drone não sai."

### "Por que greedy funciona?"
> "GPS garante progresso. Localmente ótimo é globalmente ótimo aqui porque o espaço é convexo (estamos sempre perto do melhor caminho)."

### "Qual a diferença entre normal e priority?"
> "Normal: 1 turno. Priority: 1 turno também, mas ganha desconto de 0.1 na distância virtual, então é preferido quando ambos levam 1 turno."

### "E restricted?"
> "2 turnos. Drone fica voando por 2 turnos. No turno N sai, turno N+1 ainda voando, turno N+2 chega. Ocupa a conexão esse tempo todo."

### "Como o visual funciona?"
> "Pygame mostra o grafo em cores. Drones como círculos. Interpola a posição enquanto voam (LERP). Mostra o turno atual no canto."

---

## DICAS

1. **Pratique a história de 5 minutos até saber de cor**
2. **Tenha 3 exemplos prontos**:
   - Linear path (mais simples)
   - Simple fork (dois caminhos)
   - Algo com restricted zone
3. **Seja preparado para live coding**:
   - Implementar `--capacity-info` flag
   - Mostra quantos drones em cada zona/conexão
4. **Fale com confiança**: Você entende o código melhor que qualquer um

---

**VOCÊ CONSEGUE! 🚀**
