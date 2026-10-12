# Icarus

Icarus é um agente de coaching de treino resistido baseado em ciência, com foco em praticantes naturais e personalidade inspirada no conteúdo educacional de Ícaro Lermen.

O uso principal é pelo **Claude Code** (CLI, app desktop/celular ou sessão cloud em claude.ai/code) com este repositório privado `GuilhermeMendesRosa/icarus` clonado. Instruções, conhecimento **e** memória de treino ficam no próprio repositório: cada treino é registrado em `training/data/` e persistido por commit + push na `main`.

## Como funciona

Ao abrir uma sessão do Claude Code no repositório:

- `CLAUDE.md` carrega `AGENTS.md` (identidade, comportamento e invariantes) e as regras específicas do Claude Code;
- `.claude/skills/` aponta para `.agents/skills/`, então `icarus-coaching`, `icarus-evidence` e `icarus-corpus` ficam disponíveis como skills;
- `knowledge/INDEX.md` faz o roteamento do conhecimento;
- `.agents/skills/icarus-coaching/scripts/icarus_tracker.py` lê e grava perfil, programa e sessões em `training/data/`, conforme `.agents/skills/icarus-coaching/references/repo-memory.md`;
- `.claude/settings.json` libera sem prompt os comandos do tracker e o commit/push dos dados de treino.

## Estrutura

```text
CLAUDE.md                 entrada do Claude Code (importa AGENTS.md)
AGENTS.md                 identidade, comportamento e invariantes
knowledge/                sínteses, evidência, segurança e roteamento
icaro/                    transcrições originais e artefatos derivados
training/
  SCHEMA.md               contrato dos dados
  README.md               arquitetura da memória e fluxo na academia
  data/                   memória persistente (perfil, programa, logs)
  tests/                  testes do tracker
.agents/skills/
  icarus-coaching/        criação, acompanhamento ao vivo e evolução
  icarus-evidence/        perguntas conceituais e checagem científica
  icarus-corpus/          ingestão e manutenção das transcrições
.claude/
  skills -> ../.agents/skills
  settings.json           permissões do fluxo de treino
exports/                  bootstraps legados (Projeto do Claude com Notion, ChatGPT)
```

## Treino ao vivo

1. “Icarus, qual é o treino de hoje?” — atualiza a `main`, valida e mostra a sessão com o histórico comparável.
2. “Começa o treino.” — abre a sessão.
3. `80 8 2` ou “Supino: 80 kg, 8 reps, 2 RIR.” — registra a série localmente e mostra quanto falta e o descanso.
4. “Terminei. RPE 8, 60 minutos.” — finaliza, valida, faz commit e push na `main`. Só então o Icarus diz que salvou.

Sessões cloud são efêmeras: o Icarus não encerra uma sessão finalizada sem confirmar o push.

## Memória persistente

- `training/data/profile.json`;
- `training/data/active_program.json`;
- `training/data/logs/YYYY/MM/*.jsonl`.

Esses dados são versionados intencionalmente porque este repositório é privado e o proprietário autorizou o uso como backend pessoal do Icarus. Não torne o repositório público sem antes remover os dados e considerar o histórico Git.

Validação local:

```bash
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py validate
python3 -m unittest discover -s training/tests
```

## Backends legados

- **Projeto do Claude + Notion** (2026-10-06 a 2026-10-12): `exports/claude/PROJECT_INSTRUCTIONS.md` e `references/notion-memory.md`. O Notion ficou só como arquivo, com o mesmo conteúdo do repositório.
- **ChatGPT + GitHub**: `exports/chatgpt/PROJECT_INSTRUCTIONS.md` e `references/github-memory.md`.

## Exemplos de uso

- “Icarus, qual é o treino de hoje?”
- “Começa o treino.”
- “Supino: 80 kg, 8 reps, 2 RIR.”
- “Corrige a última: eram 82,5 kg.”
- “Terminei. RPE 8, 60 minutos.”
- “Como evoluí no supino?”
- “Audite meu treino e descubra o principal gargalo.”
- “O que o corpus diz sobre volume para naturais e o que a ciência atual diz?”

No Claude Code, também dá para invocar as skills explicitamente com `/icarus-coaching`, `/icarus-evidence` ou `/icarus-corpus`.
