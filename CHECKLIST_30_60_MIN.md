# Checklist de 30–60 min (conformidade rápida)

Objetivo: fechar os principais pontos obrigatórios do PDF sem mexer na arquitetura inteira.

## 0–10 min: Entrega obrigatória da raiz
1. Criar `README.md` na raiz com:
   - primeira linha em itálico no formato 42;
   - seções: `Description`, `Instructions`, `Resources`;
   - resumo da estratégia do algoritmo;
   - descrição da visualização.
2. Criar `Makefile` com alvos:
   - `install`, `run`, `debug`, `clean`, `lint` (e opcional `lint-strict`).

## 10–25 min: Corrigir saída obrigatória da simulação
3. Separar claramente dois modos:
   - modo CLI (avança automático e imprime saída textual oficial);
   - modo visual (pygame interativo).
4. No modo CLI, imprimir somente linhas de turno (sem banners extras).
5. Corrigir regra `restricted` em trânsito:
   - enquanto está voando, saída deve ser `D<ID>-<connection>`.

## 25–40 min: Remover turno fantasma final
6. Ajustar lógica do turno para não gerar linha vazia final:
   - só contar/imprimir turno se houver movimento real;
   - ou reorganizar atualização para não criar ciclo de “apenas pouso sem movimento”.
7. Validar em 3 mapas rápidos:
   - `maps/easy/01_linear_path.txt`
   - `maps/hard/03_ultimate_challenge.txt`
   - `maps/challenger/01_the_impossible_dream.txt`

## 40–55 min: Visual e consistência
8. Completar fallback de cores para nomes não mapeados (ex.: `lime`) no terminal e no visualizador.
9. Garantir que mapas sem cor continuam legíveis.

## 55–60 min: Sanidade final
10. Rodar todos os mapas e anotar turnos finais.
11. Conferir que não existe `empty_turn` no último turno.
12. Conferir que a saída do CLI está no formato do PDF.

---

## Critério de pronto (rápido)
- Existe `README.md` na raiz.
- Existe `Makefile` com os alvos obrigatórios.
- Sem turno fantasma final.
- `restricted` em trânsito imprimindo `D<ID>-<connection>`.
- Modo CLI produz saída textual limpa conforme enunciado.
