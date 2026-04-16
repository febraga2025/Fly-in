# Relatório de Pendências (sem considerar flake8/mypy)

Data: 2026-04-16
Escopo: requisitos do PDF `Fly-in v1.2`, **excluindo** erros de lint (`flake8`) e tipagem (`mypy`).

## Resposta curta: já atende os requisitos?
**Ainda não 100%.**
Seu projeto está forte na parte de simulação e performance, mas ainda há pendências obrigatórias de entrega/formato.

---

## O que já está atendido

1. **Parser funcional com validações principais**
   - `nb_drones` na primeira linha.
   - Start e end únicos.
   - Nome de zona sem `-`.
   - Conexão duplicada (`a-b`/`b-a`) bloqueada.
   - Tipos de zona (`normal|blocked|restricted|priority`) validados.
   - Capacidades positivas validadas.

2. **Regras de ocupação e capacidade (simulação)**
   - Ocupação de zona respeitada (exceto start/end).
   - `max_link_capacity` respeitado.
   - Movimentação simultânea com controle de conflito.

3. **Performance nos mapas oficiais (`maps/**/*.txt`)**
   - Easy: `5`, `6`, `7` turnos (dentro das metas).
   - Medium: `9`, `17`, `8` turnos (dentro das metas).
   - Hard: `15`, `19`, `27` turnos (dentro das metas).
   - Challenger `01_the_impossible_dream.txt`: **44 turnos** (bate objetivo `< 45`).

4. **Visualização existe**
   - Há visualização gráfica (`pygame`) em `visualizer/vizu.py`.
   - Há tentativa de cor no terminal em `simulation.py`.

5. **`.gitignore` existe**
   - O arquivo está presente e cobre artefatos Python/venv/cache.

---

## O que falta (obrigatório no PDF)

1. **`README.md` na raiz do repositório**
   - Status: **faltando**.
   - Observação: existe `maps/README.md`, mas o requisito pede `README.md` no root com formato específico da 42.

2. **`Makefile` obrigatório**
   - Status: **faltando**.
   - Deve ter ao menos: `install`, `run`, `debug`, `clean`, `lint` (e opcional `lint-strict`).

3. **Saída de simulação estritamente conforme especificação**
   - Status: **pendente**.
   - Pontos:
     - Durante voo para zona `restricted`, seu código também imprime `D<ID>-<zone>` no turno intermediário; o PDF define `D<ID>-<connection>` enquanto estiver em trânsito.
     - O `main.py` atual roda em modo visual interativo (tecla) e não em fluxo terminal automático fim-a-fim, o que pode conflitar com avaliação de output textual esperado.

4. **Turno fantasma no fim da simulação**
    - Status: **confirmado**.
    - Evidência técnica: em todos os mapas oficiais, existe 1 turno final sem movimentos (`empty_turn`) exatamente no último turno reportado.
    - Exemplos observados:
       - `maps/easy/01_linear_path.txt`: `turns=5`, `empty_turns=[5]`
       - `maps/hard/03_ultimate_challenge.txt`: `turns=27`, `empty_turns=[27]`
       - `maps/challenger/01_the_impossible_dream.txt`: `turns=44`, `empty_turns=[44]`
    - Impacto: o número total de turnos exibido fica +1 em relação aos turnos com movimento efetivo.

5. **Docstrings PEP 257 completas em funções/classes**
   - Status: **parcial**.
   - Há docstrings em alguns pontos, mas não de forma consistente em todas as funções/classes públicas.

---

## Pendências recomendadas (não bloqueio direto, mas importantes)

1. **Cobertura de cores dos mapas**
   - Você comentou isso e está certo: atualmente há mapeamento parcial de cores.
   - Exemplo: em mapas com cores não mapeadas (ex.: `lime`), o visual cai em fallback.
   - Para aderir melhor ao enunciado (“qualquer string válida”), convém padronizar fallback de cor no terminal e no visualizador.

2. **Testes automatizados**
   - Não encontrei suíte `pytest`/`unittest` no projeto.
   - É guideline recomendado e ajuda muito na peer-review.

---

## Prioridade sugerida (ordem de ação)

1. Criar `README.md` raiz no formato exigido pela 42.
2. Criar `Makefile` com os targets obrigatórios.
3. Ajustar modo de execução para ter saída terminal automática de ponta a ponta.
4. Corrigir formato de saída no caso `restricted` em trânsito (`connection` vs `zone`).
5. Completar docstrings PEP 257.
6. Completar cobertura de cores/fallbacks.

---

## Conclusão
Sem considerar `flake8`/`mypy`, você está **bem avançado** em lógica e performance (inclusive challenger), mas **a entrega ainda não está completamente conforme** por causa de itens obrigatórios de estrutura/documentação/saída.
