---
name: icarus-coaching
description: Monta, adapta, acompanha e audita treinos de musculação para naturais, com memória de cargas e evolução. Use para ficha, treino do dia, registro de séries, progressão, volume, periodização ou estagnação; não use para perguntas puramente conceituais sem contexto pessoal.
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

## Modo parceiro ao vivo

Quando o usuário perguntar o treino do dia, iniciar/encerrar uma sessão, ditar uma série ou pedir evolução:

1. Leia [references/live-workout.md](references/live-workout.md).
2. Use exclusivamente `.agents/skills/icarus-coaching/scripts/icarus_tracker.py` para operações no histórico.
3. O comando `today` é a fonte do treino atual; `start`, `log-set`, `correct-last-set`, `finish` e `cancel` registram eventos; `progress` calcula tendência; `validate` confere integridade.
4. Confirme uma gravação somente após retorno bem-sucedido.
5. Se o CLI indicar onboarding pendente, conduza-o antes do primeiro treino e valide o programa.

## Regras

- Não trate uma faixa de volume do corpus como prescrição universal.
- Toda ficha inclui progressão, esforço, descanso, alternativas, métricas e revisão.
- Prioridade muscular deve aparecer na frequência, ordem, seleção ou volume — não apenas no texto.
- Técnicas como top set, back-off, cluster e drop são opcionais e precisam de finalidade.
- Se houver dor, doença, retorno ou população especial, leia `knowledge/SAFETY.md` e reduza o escopo.
- Quando atribuir um princípio ao corpus, confirme a fonte em `knowledge/SOURCES.md`.
- Não use memória conversacional como substituto de `training/data/`.
