# Icarus — contexto portátil legado

Este arquivo era usado pela versão antiga do Projeto do ChatGPT, quando o agente não acessava o repositório nem tinha memória persistente própria.

**Não use este arquivo como fonte principal do Icarus.**

O fluxo atual é ChatGPT-first e usa diretamente o repositório privado `GuilhermeMendesRosa/icarus`:

- `AGENTS.md` — identidade e invariantes;
- `knowledge/INDEX.md` — roteamento;
- `.agents/skills/` — fluxos operacionais;
- `training/data/` — perfil, programa e histórico persistente;
- `.agents/skills/icarus-coaching/references/github-memory.md` — backend de memória no GitHub.

Para configurar um Projeto do ChatGPT, use `exports/chatgpt/PROJECT_INSTRUCTIONS.md`.

Este arquivo permanece apenas para evitar que referências antigas quebrem; ele não deve duplicar regras, perfil, programa ou histórico.
