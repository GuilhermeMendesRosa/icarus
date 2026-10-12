# Memória de treino do Icarus

Esta pasta transforma o Icarus em um parceiro de treino persistente. O programa ativo define o que fazer; cada interação na academia gera um evento; os relatórios são calculados a partir do histórico persistido, sem depender da memória da conversa entre sessões.

Desde 2026-10-12, o Icarus roda no **Claude Code** com este repositório clonado. Cada série é gravada localmente pelo tracker na hora do relato; ao finalizar, cancelar ou em checkpoint, o agente faz commit de `training/data/` e push na `main`.

## Arquitetura

```text
training/
  templates/                    modelos versionados
  data/                         dados pessoais persistidos no repo privado
    profile.json                perfil, disponibilidade e objetivos
    active_program.json         rotação e sessões ativas
    logs/YYYY/MM/*.jsonl        eventos append-only de cada treino
    reports/                    relatórios gerados, quando usados
  SCHEMA.md                     contrato dos dados
  tests/                        testes do tracker
.agents/skills/icarus-coaching/
  references/repo-memory.md     backend canônico (Claude Code)
  references/github-memory.md   backend legado (ChatGPT) e regras de comparabilidade
  references/notion-memory.md   backend legado (Notion), só arquivo
  scripts/icarus_tracker.py     implementação das operações
```

Os logs são append-only. Um treino finalizado não deve ser reescrito; correções entram como novos eventos `set_corrected`. `exercise_id` identifica uma combinação estável de exercício, máquina/implemento e forma de contabilizar a carga.

## Fonte canônica

A branch `main` do repositório privado `GuilhermeMendesRosa/icarus` é a fonte persistente canônica. Um dado só está salvo depois que o push para `origin/main` retornou sucesso.

Histórico de backends: Codex local → ChatGPT com commits no GitHub → Notion (2026-10-06 a 2026-10-12) → Claude Code com o repositório (atual). Na volta do Notion, o conteúdo era idêntico ao de `training/data/` (5 sessões até 2026-09-30), então não houve migração de dados.

O proprietário autorizou explicitamente o versionamento de `training/data/` neste repositório privado. Não torne o repositório público sem antes remover os dados pessoais e considerar a reescrita do histórico Git.

## Uso na academia

Em uma sessão do Claude Code neste repositório:

1. “Icarus, qual é o treino de hoje?” → `git pull origin main`, `validate`, `today`.
2. “Começa o treino. Prontidão 8, dormi 7 horas.” → `start`.
3. “Primeira do supino: 80 kg, 8 reps, 2 RIR.” ou só `80 8 2` → `log-set`.
4. “Corrige a última: eram 82,5.” → `correct-last-set`.
5. “Terminei. RPE da sessão 8, 64 minutos.” → `finish` + commit + push.

Se o usuário pedir “salva até aqui”, o agente faz um checkpoint (commit + push) e continua a sessão.

Detalhes em `.agents/skills/icarus-coaching/references/repo-memory.md`.

## Operações

```bash
T=.agents/skills/icarus-coaching/scripts/icarus_tracker.py
python3 $T validate          # integridade de perfil, programa e eventos
python3 $T today             # sessão atual/próxima e histórico relevante
python3 $T start             # session_started
python3 $T log-set ...       # set_logged
python3 $T correct-last-set  # set_corrected, sem apagar o original
python3 $T finish            # session_completed
python3 $T cancel --reason   # session_cancelled; não avança rotação
python3 $T progress          # evolução entre exposições comparáveis
python3 -m unittest discover -s training/tests
```

## Concorrência e segurança de escrita

Se o push for rejeitado porque a `main` avançou, faça `git pull --rebase origin main`, rode `validate` e repita. Nunca resolva conflito apagando ou reescrevendo eventos já persistidos; reconcilie por `event_id`.

Treino finalizado é imutável. Uma sessão cancelada não avança a rotação.

## Privacidade

`training/data/` pode conter perfil, peso, desempenho, RIR, dor e notas pessoais. Esses dados estão versionados **somente porque o repositório é privado e o proprietário autorizou este uso**.

Não publique esses arquivos, não os copie para repositório público e não os mova para outro serviço sem pedido explícito.
