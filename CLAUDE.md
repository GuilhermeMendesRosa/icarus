@AGENTS.md

## Claude Code

Este repositório é o ambiente canônico do Icarus. Instruções, conhecimento e memória de treino vivem aqui; não use Notion nem outro serviço para gravar treinos.

- Skills: `.claude/skills` aponta para `.agents/skills` (`icarus-coaching`, `icarus-evidence`, `icarus-corpus`).
- Memória de treino: siga `.agents/skills/icarus-coaching/references/repo-memory.md`. Use o tracker `.agents/skills/icarus-coaching/scripts/icarus_tracker.py` para `today`, `start`, `log-set`, `correct-last-set`, `finish`, `cancel`, `progress` e `validate`; não escreva JSONL à mão.
- Ao começar um treino, `git pull origin main` antes de `today`.
- Registre cada série localmente na hora do relato; não faça commit por série.
- Em `finish`, `cancel` ou "salva até aqui": `validate` + testes do tracker → commit só de `training/data/` (`training: finish <session_id>`) → `git push -u origin main` (retry 2s/4s/8s/16s em falha de rede). Dados de treino vão direto na `main`, por decisão do proprietário; mudanças de instruções seguem o fluxo normal de branch.
- A sessão cloud é efêmera: nunca encerre um treino finalizado, cancelado ou com checkpoint pedido sem push confirmado, e nunca diga "salvo" antes disso.
- Respostas durante o treino são lidas no celular entre séries: curtas, no formato de `references/live-workout.md`.
