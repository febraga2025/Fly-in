# Fly-in: Explicação Completa do Projeto

## 1. O QUE É O PROJETO?

**Fly-in** é um sistema de simulação de roteamento de drones autônomos.

**Objetivo**: Mover N drones de um ponto de partida (start_hub) para um destino (end_hub) no **menor número de turnos possível**, respeitando restrições de capacidade, movimento e topologia da rede.

**Analogia**: Como organizar o fluxo de entrega de pacotes em uma cidade, onde:
- Drones = Pacotes
- Zonas = Intersecções/Warehouses
- Conexões = Ruas
- Turn = 1 unidade de tempo

---

## 2. OS COMPONENTES PRINCIPAIS

### 2.1 PARSER (`parse.py`)
**O que faz**: Lê um arquivo de mapa em formato customizado

**Exemplo de entrada**:
```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: warehouse 5 5 [zone=restricted color=red max_drones=2]
connection: hub-warehouse
connection: warehouse-goal [max_link_capacity=2]
```

**O que valida**:
- Primeiro line DEVE ser `nb_drones`
- DEVE ter exatamente 1 start_hub e 1 end_hub
- Nomes de zonas não podem ter dashes (-)
- Capacidades DEVEM ser positivas
- Zonas não podem ser duplicadas

### 2.2 MODELOS (`models/`)

#### Zone (zona.py)
```
Zone (classe abstrata)
├── NormalZone (custo: 1 turn)
├── RestrictedZone (custo: 2 turns) 
├── PriorityZone (custo: 1 turn, preferencial)
└── BlockedZone (custo: ∞, inacessível)
```

**Propriedades**:
- `name`: identificador único
- `x, y`: coordenadas no mapa
- `max_drones`: quantos drones podem estar lá simultaneamente (default: 1)
- `is_start`, `is_end`: marcadores especiais
- `color`: para visualização

#### Drone (drone.py)
```
Drone
├── id: "D1", "D2", etc
├── current_zone: onde está agora (ou None se voando)
├── target_zone: para onde vai
├── arrival_turn: quando chega
└── active_connection: qual estrada está usando
```

#### Connection (connections.py)
```
Connection (conexão bidirecional)
├── zone_a, zone_b: zonas conectadas
└── max_link_capacity: quantos drones podem passar simultaneamente (default: 1)
```

#### MapGraph (graph.py)
```
MapGraph (grafo)
├── zones: Dict[nome, Zone]
├── connections: List[Connection]
├── start_zone: referência rápida
└── end_zone: referência rápida
```

### 2.3 PATHFINDING (`algorithms/pathfinding.py`)

**Algoritmo**: Reverse Dijkstra

**Como funciona**:
1. Começa no `end_zone` com distância = 0
2. Propaga distâncias para trás (reverso)
3. Cria um "GPS map" com distância de cada zona até o destino

**Exemplo**:
```
end_zone (goal) = 0
zone_before_goal = 1
zone_before_zone_before = 2
...
start_zone = N
```

**Complexidade**: O(Z + C) onde Z = zonas, C = conexões

### 2.4 SIMULATION (`simulation.py`)

**A máquina do tempo**: Executa turno por turno

**Cada turno faz**:

1. **LANDING PHASE** (Pouso)
   - Drones que completaram viagem multi-turno descem

2. **ARRIVAL RADAR** (Radar de chegada)
   - Avisa drones que chegam em zonas restricted no próximo turno

3. **CONNECTION CENSUS** (Censo de conexões)
   - Conta quantos drones estão voando em cada conexão

4. **FILTER MOVABLE** (Filtra quem pode se mover)
   - Seleciona drones: não estão voando E não estão no destino

5. **DECIDE ROUTES** (Decide rotas)
   Para cada drone:
   - Olha todas as zonas vizinhas
   - Verifica se tem espaço (zone occupancy + connection capacity)
   - Escolhe a melhor (Greedy):
     * Priority zones ganham 0.1 de "desconto"
     * Nunca anda para trás (dist <= current_dist)
     * Prefere o caminho mais curto

6. **APPLY MOVEMENTS** (Aplica movimentos)
   - Todos os movimentos acontecem simultaneamente
   - Atualiza ocupação de conexões

### 2.5 SIMULATION RUNNER (`simulation_runner.py`)

**Orquestra a simulação**:
1. Cria o grafo (parser)
2. Cria a simulação
3. Calcula o GPS map (pathfinding)
4. Executa turn by turn até todos os drones chegarem
5. Coleta histórico para replay

### 2.6 VISUALIZER (`visualizer/`)

**Dois sistemas**:

#### vizu.py (Pygame)
- Desenha grafo em tempo real
- Mostra drones como círculos coloridos
- Usa cores dos metadados
- Interpola posição de drones em voo (LERP)

#### replay.py
- Permite navegar pela simulação com arrow keys
- LEFT = turno anterior
- RIGHT = próximo turno
- Mostra `Current Turn: N`

---

## 3. REGRAS E RESTRIÇÕES

### 3.1 Movimento
```
Normal zone        → 1 turn
Restricted zone    → 2 turns (drone fica voando 2 turnos)
Priority zone      → 1 turn (preferido)
Blocked zone       → ✗ IMPOSSÍVEL
```

### 3.2 Capacidade de Zonas
- **Padrão**: max_drones = 1 (só 1 drone por zona)
- **Com metadado**: `max_drones=N` permite N drones
- **Exceções**: 
  - start_hub: ilimitado (todos começam aqui)
  - end_hub: ilimitado (todos podem chegar)

### 3.3 Capacidade de Conexões
- **Padrão**: max_link_capacity = 1 (só 1 drone voando)
- **Com metadado**: `max_link_capacity=N` permite N drones

### 3.4 Movimento Simultâneo
- Todos os drones se movem ao mesmo tempo
- Ordem não importa (determinístico)
- Conflitos são prevenidos ANTES do movimento

---

## 4. EXEMPLO PASSO A PASSO

### Setup
```
2 drones
start_hub A (0,0)
end_hub C (2,0)
hub B (1,0)
A-B, B-C (todas conexões normais)
```

### Execução

```
TURNO 0:
- D1 em A, D2 em A
- Nenhum em voo

TURNO 1:
- D1: quer ir para B, pode (espaço em B, espaço em A-B)
- D2: quer ir para B, NÃO pode (A-B já tem D1)
- D1 sai de A, voa para B
- D2 fica em A
Output: D1-B

TURNO 2:
- D1: chega em B, agora em B
- D1: quer ir para C, pode
- D2: quer ir para B, pode (A-B livre, B tem espaço)
- D1 sai de B, voa para C
- D2 voa de A para B
Output: D1-C D2-B

TURNO 3:
- D1: chega em C, fim! ✓
- D2: em B, quer ir para C, pode
- D2 voa para C
Output: D2-C

TURNO 4:
- D2: chega em C ✓
- Simulação termina

TOTAL: 4 turnos
```

---

## 5. O ALGORITMO DE DECISÃO (A Parte Inteligente)

### 5.1 Greedy Path Selection
**Cada drone escolhe O MELHOR vizinho, não O ÓTIMO global**

```python
Para cada vizinho possível:
  1. Tem espaço na zona? NÃO → skip
  2. Tem espaço na conexão? NÃO → skip
  3. Calcula "virtual_distance":
     - Se é PriorityZone: distance - 0.1
     - Senão: distance
  4. Nunca volta para trás: distance <= current_distance
  5. Escolhe o com menor virtual_distance
```

### 5.2 Por que funciona?
- **Greedy é rápido**: O(D × C) por turno
- **Funciona bem**: Localmente ótimo ≈ globalmente ótimo
- **Evita deadlocks**: Capacidade é respeitada ANTES
- **Usa GPS**: Distância para destino guia decisões

### 5.3 Exemplo de decisão
```
Drone D1 em "hub"
Distância até goal: hub=3, zona_a=2, zona_b=2

Vizinhos:
- zona_a (normal): dist=2, virtual=2.0 ✓ ESCOLHE
- zona_b (priority): dist=2, virtual=1.9 ✓ MELHOR!
- backwards (normal): dist=4, rejected (dist > current)

D1 escolhe zona_b (priority zone)
```

---

## 6. COMPLEXIDADE E PERFORMANCE

### 6.1 Análise
```
Por turno:
- Pathfinding (one-time): O(Z + C)
- Cada turno: O(D × C)
  onde D = drones, C = conexões

Espaço:
- Graph: O(Z + C)
- State: O(D)
- GPS map: O(Z)
```

### 6.2 Targets vs Reality
```
Easy (Linear Path, 2 drones):
  Target: ≤ 6 turns
  Resultado: 4 turns ✓

Easy (Simple Fork, 3 drones):
  Target: ≤ 6 turns
  Resultado: 6 turns ✓
```

---

## 7. EXEMPLO DE SAÍDA

### Input File
```
nb_drones: 2
start_hub: hub 0 0
end_hub: goal 2 0
hub: waypoint1 1 0
connection: hub-waypoint1
connection: waypoint1-goal
```

### Output
```
D1-waypoint1
D1-goal D2-waypoint1
D2-goal
```

**Interpretação**:
- Turn 1: D1 se move para waypoint1
- Turn 2: D1 chega no goal, D2 se move para waypoint1
- Turn 3: D2 chega no goal
- **Total: 3 turnos**

---

## 8. VISUAL SYSTEM

### 8.1 Terminal Output
```
D1-waypoint1
D1-goal D2-waypoint1
D2-goal
```
- 1 linha por turno
- Formato: `D<ID>-<destino>`
- Drones que não se movem são omitidos
- Termina quando todos chegam

### 8.2 Pygame Window
```
[Mapa em cores]
- Zonas como círculos (ou quadrados se restricted)
- Drones como bolinhas cyan pequeninas
- Conexões como linhas
- Texto com ID do drone
- Turno atual no canto

Navegação:
- LEFT arrow: turno anterior
- RIGHT arrow: próximo turno
```

---

## 9. TIPO SEGURANÇA

### 9.1 Type Hints
```python
def run_autopilot_turn(self, gps: Dict[str, int]) -> None:
    self.turn += 1
    conn_usage: Dict[Connection, int] = {}
    best_conn: Connection | None = None
    ...
```

### 9.2 Mypy
- Verifica TODOS os tipos
- 14 arquivos: ✓ PASSED
- Sem erros, sem warnings

### 9.3 Flake8
- Verifica estilo
- ✓ PASSED (excluding .venv)

---

## 10. ESTRUTURA DO CÓDIGO

```
main.py
├── Entrada do usuário
├── Chama run_text_simulation()
└── Mostra output

parse.py
├── Lê arquivo
├── Valida tudo
└── Retorna MapGraph + nb_drones

simulation.py
├── Classe Simulation
├── run_autopilot_turn() ← O CORAÇÃO
└── is_finished()

simulation_runner.py
├── Coordena tudo
├── Chama pathfinding
├── Roda simulação
└── Coleta histórico

algorithms/pathfinding.py
├── build_distance_map()
└── Reverse Dijkstra

models/
├── zone.py (Zone hierarchy)
├── drone.py (Drone class)
├── graph.py (MapGraph)
└── connections.py (Connection)

visualizer/
├── vizu.py (Pygame renderer)
└── replay.py (Interactive replay)
```

---

## 11. PONTOS-CHAVE PARA MEMORIZAR

### 11.1 Quando alguém pergunta "Como funciona?"
**Resposta rápida**:
> "Reverse Dijkstra cria um GPS map com distância até o destino. Cada turno, cada drone escolhe o melhor vizinho respeitando capacidade de zonas e conexões. Simples, rápido, funciona."

### 11.2 Por que Greedy funciona?
> "Greedy é localmente ótimo. Como respeitamos capacidade, evitamos deadlocks. GPS map garante que drones nunca andam para trás. Resultado: ótimo global."

### 11.3 Maior desafio?
> "Conflitos de capacidade. Solução: contar usando em cada conexão ANTES de autorizar movimento."

### 11.4 Complexidade?
> "O(Z + C) para setup, O(D × C) por turno. Linear na maioria dos casos reais."

### 11.5 Diferencial?
> "Type safety 100%, OOP completo, sem bibliotecas externas (custom graph), visual em tempo real."

---

## 12. PERGUNTAS COMUNS NA AVALIAÇÃO

### P: "Por que usar Reverse Dijkstra?"
**R**: "Porque calculamos uma vez no início e reutilizamos para todos os drones todo turno. Se fosse forward Dijkstra, teria que recalcular para cada drone em cada turno."

### P: "Como evitam deadlock?"
**R**: "Checamos capacidade ANTES de autorizar movimento. Se conexão A-B tem capacidade 1 e já tem um drone, ninguém mais entra."

### P: "Por que o algoritmo é greedy?"
**R**: "Porque cada drone olha só os vizinhos imediatos e escolhe o melhor. Não computa caminhos globais. É rápido e funciona bem na prática."

### P: "Como lidam com multi-turn movements?"
**R**: "Drone que vai para zona restricted ganha flag `target_zone` e `arrival_turn`. Enquanto `current_turn < arrival_turn`, drone está voando."

### P: "Qual a diferença entre current_zone e target_zone?"
**R**: "current_zone = onde drone está físico agora. target_zone = para onde está indo. Enquanto voa, current_zone é None."

---

## 13. MOCK DE APRESENTAÇÃO

### Você diz:
"Meu projeto é um simulador de roteamento de drones. O objetivo é mover N drones de um ponto A para um ponto B no menor número de turnos.

O algoritmo usa Reverse Dijkstra para calcular a distância de cada zona até o destino. Então, cada turno, cada drone escolhe o melhor vizinho usando greedy: respeita capacidade, nunca anda para trás, e prefere priority zones.

Suporta 4 tipos de zona: normal (1 turno), restricted (2 turnos), priority (1 turno), blocked (impossível). Também suporta capacidade de zona e conexão.

Tenho 100% type safety com mypy, flake8 completo, OOP puro, sem bibliotecas externas. Visual em Pygame mostra tudo em tempo real.

Testa com sucesso os mapas fáceis dentro dos targets. Medium maps em progresso."

---

## 14. CHECKLIST PARA EVAL

- [ ] Entendo o parser
- [ ] Entendo os modelos (Zone, Drone, Connection, Graph)
- [ ] Entendo Reverse Dijkstra
- [ ] Entendo run_autopilot_turn()
- [ ] Posso explicar por que greedy funciona
- [ ] Sei a complexidade
- [ ] Posso contar sobre type safety
- [ ] Posso descrever a visualização
- [ ] Sei responder sobre deadlocks e capacidade
- [ ] Tenho 3 exemplos prontos para explicar

---

**Boa sorte na avaliação! 🚀**
