# Memória de treino do Icarus

Esta pasta transforma o Icarus em um parceiro de treino persistente. O programa ativo define o que fazer; cada interação na academia gera um evento; os relatórios são calculados a partir do histórico, sem depender da memória da conversa.

## Arquitetura

```text
training/
  templates/                    modelos versionados
  data/                         dados pessoais locais, ignorados pelo Git
    profile.json                perfil, disponibilidade e objetivos
    active_program.json         rotação e sessões ativas
    logs/YYYY/MM/*.jsonl        eventos de cada treino
    reports/                    relatórios gerados
  SCHEMA.md                     contrato dos dados
.agents/skills/icarus-coaching/
  scripts/icarus_tracker.py     CLI usada pelo agente
```

Os logs são append-only. Um treino finalizado não deve ser reescrito; correções entram como novos eventos em versões futuras do esquema. `exercise_id` identifica uma combinação estável de exercício, máquina/implemento e forma de contabilizar a carga.

## Primeiro uso

Peça ao agente:

> Icarus, quero fazer meu onboarding como parceiro de treino.

Ele deve coletar os dados mínimos, preencher `training/data/profile.json`, criar `training/data/active_program.json`, validar e só então ativar o programa. Os arquivos são criados automaticamente a partir dos templates se estiverem ausentes.

## Uso na academia

No Codex Remote do celular, usando o mesmo computador e projeto:

1. “Icarus, qual é o treino de hoje?”
2. “Começa o treino. Prontidão 8, dormi 7 horas.”
3. “Primeira do supino: 80 kg, 8 reps, 2 RIR.”
4. “Segunda: 80 por 7, 1 RIR.”
5. “Terminei. RPE da sessão 8, 64 minutos.”

O agente confirma cada gravação e compara apenas com exposições compatíveis.

## Comandos operacionais

```bash
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py init
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py today
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py start --readiness 8 --sleep-hours 7
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py log-set --exercise supino-reto --weight 80 --reps 8 --rir 2
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py correct-last-set --weight 82.5 --reason "carga ditada errada"
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py finish --session-rpe 8 --duration-minutes 64
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py progress
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py validate
```

O usuário não precisa digitar comandos. A skill traduz linguagem natural e executa a operação correta.

## Remote, nuvem e persistência

O fluxo principal pressupõe Codex Remote conectado ao computador onde este projeto está salvo. Se usar um chat em ambiente cloud, o repositório é clonado em um container e as gravações aparecem como mudanças da tarefa; elas não chegam automaticamente ao diário local até que o diff seja aplicado ou integrado.

Os dados pessoais ficam ignorados pelo Git por padrão. Para backup ou uso em mais de um computador, escolha conscientemente uma solução privada e segura. Não publique `training/data/` em repositório público.
