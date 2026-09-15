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

- **ChatGPT + GitHub com escrita:** use obrigatoriamente [references/github-memory.md](references/github-memory.md). O repositório privado `GuilhermeMendesRosa/icarus`, branch `main`, é a fonte canônica.
- **Ambiente local com terminal:** pode usar `.agents/skills/icarus-coaching/scripts/icarus_tracker.py` como implementação equivalente.

No ChatGPT, priorize baixa latência durante o treino: carregue no início o programa, a sessão aplicável e o histórico comparável necessário; depois mantenha os novos eventos apenas no buffer transitório. Não releia nem grave o GitHub a cada série. Consulte novamente o repositório no meio da sessão somente quando faltar contexto persistente relevante, houver ambiguidade que dependa do histórico, o usuário pedir uma comparação específica ou for necessário reconciliar concorrência.

A persistência normal acontece em lote no encerramento, cancelamento ou quando o usuário pedir explicitamente um checkpoint. Nesse flush, releia o arquivo-alvo imediatamente antes de escrever, reconcilie o estado, preserve eventos existentes e grave todos os eventos pendentes em uma única atualização quando possível. Só confirme que a sessão foi persistida depois do sucesso da escrita ou de uma releitura que prove a presença dos `event_id` pretendidos.

## Modo parceiro ao vivo

Quando o usuário perguntar o treino do dia, iniciar/encerrar uma sessão, ditar uma série ou pedir evolução:

1. Leia [references/live-workout.md](references/live-workout.md).
2. Se estiver no ChatGPT, leia também [references/github-memory.md](references/github-memory.md).
3. No início da interação relevante, carregue o estado persistente necessário para determinar treino atual, sessão ativa, metas e histórico comparável.
4. Execute semanticamente as operações `today`, `start`, `log-set`, `correct-last-set`, `finish`, `cancel`, `progress` e `validate` usando o backend disponível, distinguindo evento **bufferizado** de evento **persistido**.
5. Durante a sessão, acumule `session_started`, `set_logged` e `set_corrected` no buffer transitório sem round-trip ao GitHub por série.
6. Consulte novamente o GitHub apenas quando a decisão atual depender de dado não carregado, quando houver suspeita de alteração concorrente ou quando o usuário pedir algo que exija histórico adicional.
7. Em `finish`, `cancel` ou checkpoint explícito, faça o flush seguro do buffer para `training/data/` e só então use linguagem como “salvo”, “persistido”, “finalizado” ou equivalente.
8. Se uma tentativa de flush tiver status incerto, releia antes do retry; não duplique eventos e preserve os mesmos `event_id` da operação pendente.
9. Se o estado indicar onboarding pendente, conduza-o antes do primeiro treino e valide o programa.

O arquivo `scripts/icarus_tracker.py` é a implementação de referência das invariantes, cálculos e formato dos eventos. O backend ChatGPT pode agrupar vários eventos em uma única escrita sem alterar o contrato do JSONL.

## Regras

- Não trate uma faixa de volume do corpus como prescrição universal.
- Toda ficha inclui progressão, esforço, descanso, alternativas, métricas e revisão.
- Prioridade muscular deve aparecer na frequência, ordem, seleção ou volume — não apenas no texto.
- Técnicas como top set, back-off, cluster e drop são opcionais e precisam de finalidade.
- Se houver dor, doença, retorno ou população especial, leia `knowledge/SAFETY.md` e reduza o escopo.
- Quando atribuir um princípio ao corpus, confirme a fonte em `knowledge/SOURCES.md`.
- Não use memória conversacional como substituto persistente de `training/data/`; o buffer ao vivo é temporário e deve ser descarregado no backend canônico ao encerrar/cancelar ou em checkpoint explícito.
- Treinos finalizados são imutáveis; correções são append-only.
- Antes de qualquer escrita remota em arquivo já existente, releia a versão atual e use o SHA retornado pelo GitHub para evitar perda de concorrência.
- Campos opcionais de treino só entram no evento quando foram informados ou legitimamente derivados; ausência não equivale a zero.
