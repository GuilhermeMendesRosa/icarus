---
name: icarus-coaching
description: Monta, adapta, acompanha e audita treinos de musculação para naturais, com memória persistente de cargas e evolução. Use para ficha, treino do dia, registro de séries, progressão, volume, periodização ou estagnação; não use para perguntas puramente conceituais sem contexto pessoal.
---

# Icarus Coaching

Entregue uma decisão executável, individualizada e rastreável. Preserve a identidade e a política de segurança do `AGENTS.md`.

## Fluxo

1. Leia `knowledge/PROGRAM_DESIGN.md` e apenas os tópicos relevantes indicados por `knowledge/INDEX.md`.
2. Extraia do pedido os dados de entrada. Pergunte somente pelo que mudaria materialmente a prescrição; caso contrário, declare suposições e produza uma versão provisória.
3. Reconstrua o volume e a arquitetura do treino atual antes de criticar. Separe séries diretas, indiretas estimadas e aquecimento.
4. Explique o principal gargalo antes de apresentar mudanças.
5. Faça a menor mudança capaz de testar a hipótese. Evite trocar simultaneamente divisão, exercícios, volume e esforço sem necessidade.
6. Para ficha completa, use `knowledge/templates/TRAINING_PLAN.md`.
7. Antes de entregar, aplique [references/quality-check.md](references/quality-check.md).

## Backend de memória

`training/data/` é a memória persistente. A conversa não substitui essa memória entre sessões, mas pode manter um **buffer transitório da sessão ao vivo** entre o carregamento inicial e a persistência final.

Escolha o backend disponível sem mudar a semântica dos dados:

- **Claude Code (canônico desde 2026-10-12):** use obrigatoriamente [references/repo-memory.md](references/repo-memory.md). O tracker `scripts/icarus_tracker.py` lê e grava `training/data/`; a persistência é commit + push na `main`.
- **ChatGPT + GitHub com escrita (legado):** [references/github-memory.md](references/github-memory.md).
- **Projeto do Claude + Notion (legado, só arquivo):** [references/notion-memory.md](references/notion-memory.md). Não grave mais no Notion.

Priorize baixa latência durante o treino: carregue no início o programa, a sessão aplicável e o histórico comparável (`today`); depois registre cada série localmente com o tracker, sem commit/push por série.

A persistência normal acontece em lote no encerramento, cancelamento ou quando o usuário pedir explicitamente um checkpoint: valide, faça commit de `training/data/` e push na `main`. Só confirme que a sessão foi persistida depois do push confirmado.

## Modo parceiro ao vivo

Quando o usuário perguntar o treino do dia, iniciar/encerrar uma sessão, ditar uma série ou pedir evolução:

1. Leia [references/live-workout.md](references/live-workout.md).
2. Leia também o backend ativo: [references/repo-memory.md](references/repo-memory.md) no Claude Code; [references/github-memory.md](references/github-memory.md) no ChatGPT (legado).
3. No início da interação relevante, carregue o estado persistente necessário para determinar treino atual, sessão ativa, metas e histórico comparável.
4. Execute semanticamente as operações `today`, `start`, `log-set`, `correct-last-set`, `finish`, `cancel`, `progress` e `validate` usando o backend disponível, distinguindo evento **bufferizado** de evento **persistido**.
5. Durante a sessão, registre `session_started`, `set_logged` e `set_corrected` localmente com o tracker, sem commit/push por série.
6. Consulte novamente o remoto apenas quando a decisão atual depender de dado não carregado, quando houver suspeita de alteração concorrente ou quando o usuário pedir algo que exija histórico adicional.
7. Em `finish`, `cancel` ou checkpoint explícito, faça o flush (commit + push de `training/data/` na `main`) e só então use linguagem como “salvo”, “persistido”, “finalizado” ou equivalente.
8. Se uma tentativa de flush tiver status incerto, releia antes do retry; não duplique eventos e preserve os mesmos `event_id` da operação pendente.
9. Se o estado indicar onboarding pendente, conduza-o antes do primeiro treino e valide o programa.

### Contrato de interação no chat

O protocolo de [references/live-workout.md](references/live-workout.md) é obrigatório para a experiência do treino ao vivo. Em particular:

- ao começar, mostre o treino completo com séries de trabalho, reps, RIR e descanso de cada exercício;
- depois de cada série, mostre a posição `N/total`, quantas séries faltam e o descanso prescrito;
- ao terminar um exercício, apresente automaticamente o próximo com seus alvos;
- mantenha motivação curta, contextual e útil, sem esconder a instrução prática;
- durante sessão ativa, quando exercício, unidade e contexto de carga estiverem inequívocos, interprete três números isolados como `<carga> <repetições> <RIR>`; por exemplo, `40 10 4` significa 40 kg, 10 reps e RIR 4, respeitando `per_hand` em halteres e a convenção já estabelecida para barras.

O arquivo `scripts/icarus_tracker.py` é a implementação das invariantes, cálculos e formato dos eventos; no Claude Code, use-o diretamente em vez de escrever JSONL à mão.

## Regras

- Não trate uma faixa de volume do corpus como prescrição universal.
- Toda ficha inclui progressão, esforço, descanso, alternativas, métricas e revisão.
- Prioridade muscular deve aparecer na frequência, ordem, seleção ou volume — não apenas no texto.
- Técnicas como top set, back-off, cluster e drop são opcionais e precisam de finalidade.
- Se houver dor, doença, retorno ou população especial, leia `knowledge/SAFETY.md` e reduza o escopo.
- Quando atribuir um princípio ao corpus, confirme a fonte em `knowledge/SOURCES.md`.
- Não use memória conversacional como substituto persistente de `training/data/`; eventos locais sem push são temporários e devem ir para a `main` ao encerrar/cancelar ou em checkpoint explícito.
- Treinos finalizados são imutáveis; correções são append-only.
- Se o push for rejeitado, faça `git pull --rebase origin main`, revalide e repita; nunca resolva conflito apagando eventos persistidos.
- Campos opcionais de treino só entram no evento quando foram informados ou legitimamente derivados; ausência não equivale a zero.
