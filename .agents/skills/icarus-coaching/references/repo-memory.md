# Backend de memória no repositório (Claude Code)

Este é o backend canônico do Icarus desde 2026-10-12, quando executado no **Claude Code** (CLI, app desktop/celular ou sessão cloud em claude.ai/code) com este repositório clonado. Perfil, programa e histórico ficam em `training/data/`, na branch `main`, e são lidos e gravados pelo CLI `scripts/icarus_tracker.py`.

O contrato dos dados é o de `training/SCHEMA.md`. As regras de comparabilidade, e1RM, volume e validação de [github-memory.md](github-memory.md) continuam valendo; o formato do chat ao vivo é o de [live-workout.md](live-workout.md).

## Princípio

- O tracker grava cada evento no JSONL local na hora do relato. Isso é rápido e não usa rede: o arquivo local não commitado faz o papel do buffer transitório.
- **Persistido** significa commitado e com push para `origin/main` confirmado. Antes disso, diga que a série foi registrada localmente, nunca "salvo".
- Sessões cloud são efêmeras: o container pode ser reciclado. Nunca termine uma sessão finalizada, cancelada ou com checkpoint pedido sem o push confirmado.

## Comandos

Rode sempre a partir da raiz do repositório:

```bash
T=".agents/skills/icarus-coaching/scripts/icarus_tracker.py"
python3 $T validate
python3 $T today
python3 $T start [--readiness 8] [--sleep-hours 7] [--bodyweight-kg 80] [--notes "..."]
python3 $T log-set --exercise <exercise_id> --weight 80 --reps 8 [--rir 2] [--set-type working|top|back_off|feeder] [--pain 0] [--notes "..."]
python3 $T correct-last-set [--weight 82.5] [--reps 8] [--rir 1] [--reason "..."]
python3 $T finish [--session-rpe 8] [--duration-minutes 64] [--notes "..."]
python3 $T cancel --reason "..."
python3 $T progress [--exercise <exercise_id>] [--limit 5]
```

- Passe apenas o que o usuário informou. Campo ausente fica ausente; nunca preencha 0 ou valor presumido.
- `--exercise` aceita o `exercise_id`; prefira sempre o ID exato da sessão atual.
- `unit` e `load_context` vêm do programa; só passe `--unit`/`--load-context` se o usuário indicar algo diferente, e nesse caso confirme se não seria outro `exercise_id`.
- Use os `set_type` já presentes no histórico (`working`, `top`, `back_off`, `feeder`) para manter consistência.
- Feeder/reconhecimento só entra como `--set-type feeder` quando carga e reps forem informadas; não conta como série válida.

## Fluxo ao vivo

1. **Início (`today`/`start`)**: `git pull origin main` (com retry 2s/4s/8s/16s em falha de rede), depois `validate` e `today`. Mostre o treino completo conforme `live-workout.md`. Em "começa o treino", rode `start`.
2. **Cada série (`log-set`)**: rode o comando no momento do relato e responda no formato curto do `live-workout.md` (`série N/total`, faltam, descanso, próximo). Não faça commit por série.
3. **Correção**: `correct-last-set`; o evento original continua no log.
4. **Checkpoint** ("salva até aqui"): faça o flush abaixo mantendo a sessão ativa.
5. **Fim (`finish`) ou cancelamento (`cancel`)**: rode o comando e faça o flush. Só depois do push confirmado diga "salvo/finalizado" e entregue o resumo (`progress` dos exercícios do dia, se útil) e a próxima sessão da rotação (`today`).

## Flush (commit + push na main)

```bash
python3 $T validate
python3 -m unittest discover -s training/tests -q
git add training/data
git commit -m "training: finish <session_id>"      # ou: cancel <session_id> / checkpoint <session_id>
git push -u origin main
```

- Faça commit somente de `training/data/` nesse fluxo; mudanças de instruções vão em commits separados.
- Se o push falhar por rede, repita até 4 vezes com espera de 2s, 4s, 8s e 16s.
- Se o push for rejeitado porque a `main` remota avançou: `git pull --rebase origin main`, rode `validate` de novo e repita o push. Logs são um arquivo por sessão; nunca resolva conflito apagando ou reescrevendo linhas já persistidas. Em conflito dentro do mesmo JSONL, preserve a união dos eventos por `event_id` e avise o usuário.
- Confirme com `git status -sb` (sem `ahead`) ou `git log origin/main -1` antes de dizer que salvou.
- Se não conseguir fazer push, diga claramente que os eventos estão só no container local, que podem se perder, e tente novamente antes de encerrar.

## Onboarding e mudanças de programa

- Edite `training/data/profile.json` e `training/data/active_program.json` preservando o schema.
- Novo programa: novo `program_id`; mantenha os `exercise_id` de variantes equivalentes para preservar comparabilidade. Logs antigos não são alterados.
- Rode `validate` e os testes, e faça commit + push (`training: <descrição>`) antes de declarar o programa ativo.

## Privacidade

`training/data/` só é versionado porque o repositório é privado e o proprietário autorizou. Não copie esses dados para outro serviço, repositório público ou resposta compartilhável sem pedido explícito.
