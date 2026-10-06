# Icarus

Icarus é um agente de coaching de treino resistido baseado em ciência, com foco em praticantes naturais e personalidade inspirada no conteúdo educacional de Ícaro Lermen.

O uso principal é por um **Projeto do Claude** (web, desktop ou celular). O repositório privado `GuilhermeMendesRosa/icarus` entra como conhecimento sincronizado do GitHub, com as instruções do agente e a base de conhecimento. A memória persistente de treino fica no **Notion** (`Segundo Cérebro → Icarus`).

## Como funciona

Ao iniciar uma conversa no Projeto Icarus, o agente consulta no conhecimento sincronizado:

- `AGENTS.md` para identidade, comportamento e invariantes;
- `knowledge/INDEX.md` para roteamento;
- `.agents/skills/` para o fluxo aplicável;
- o Notion, via `.agents/skills/icarus-coaching/references/notion-memory.md`, para perfil, programa ativo e histórico persistente.

O objetivo é que o chat aja como interface do agente definido no repositório, em vez de manter uma cópia separada das regras.

## Estrutura

```text
AGENTS.md                 identidade, comportamento e invariantes
knowledge/                sínteses, evidência, segurança e roteamento
icaro/                    transcrições originais e artefatos derivados
training/
  SCHEMA.md               contrato dos dados
  README.md               arquitetura da memória
  data/                   arquivo histórico (congelado em 2026-10-06; estado atual no Notion)
.agents/skills/
  icarus-coaching/        criação, acompanhamento ao vivo e evolução
  icarus-evidence/        perguntas conceituais e checagem científica
  icarus-corpus/          ingestão e manutenção das transcrições
exports/claude/
  PROJECT_INSTRUCTIONS.md setup e bootstrap do Projeto do Claude
exports/chatgpt/
  PROJECT_INSTRUCTIONS.md bootstrap do Projeto do ChatGPT (legado)
```

## Configuração recomendada no Claude

Siga `exports/claude/PROJECT_INSTRUCTIONS.md`. Em resumo: crie o Projeto **Icarus — Treino**, adicione este repositório como conhecimento via GitHub (sem `training/data/`), ligue o conector do Notion e cole o bloco de instruções. Depois de mudar regras no repo, faça push e sincronize o conhecimento do Projeto.

O backend de memória está em `.agents/skills/icarus-coaching/references/notion-memory.md`: bancos **Sessões**, **Séries**, **Prescrição** e **Exercícios**, mais as páginas **Perfil** e **Programa ativo**. Dá para acompanhar tudo também pelo app do Notion.

## Configuração no ChatGPT (legado)

1. Crie um Projeto chamado **Icarus — Treino**.
2. Conecte o GitHub com acesso ao repositório privado `GuilhermeMendesRosa/icarus`.
3. Copie o bloco de `exports/chatgpt/PROJECT_INSTRUCTIONS.md` para as instruções do Projeto.
4. Inicie um chat com algo como `Icarus, qual é meu treino hoje?`.

As instruções do Projeto são apenas um bootstrap. O comportamento real deve ser carregado da versão atual do repositório.

## Treino ao vivo no ChatGPT

O backend oficial está em:

`.agents/skills/icarus-coaching/references/github-memory.md`

Com GitHub conectado para leitura e escrita, o Icarus consegue:

- recuperar o treino atual;
- iniciar sessão;
- registrar cada série;
- corrigir série sem apagar o evento anterior;
- finalizar ou cancelar treino;
- comparar exposições equivalentes;
- acompanhar tendência e progressão entre conversas.

Cada gravação só é confirmada depois do sucesso da escrita no GitHub.

## Memória persistente

Desde 2026-10-06, a memória canônica fica no Notion (ver acima). No fluxo legado do ChatGPT, ela ficava em `training/data/`:

- `profile.json`;
- `active_program.json`;
- `logs/YYYY/MM/*.jsonl`.

Esses dados são versionados intencionalmente porque este repositório é privado e o proprietário autorizou o uso como backend pessoal do Icarus. Não torne o repositório público sem antes remover os dados e considerar o histórico Git.

## Compatibilidade local

`.agents/skills/icarus-coaching/scripts/icarus_tracker.py` permanece no projeto como implementação de referência e pode continuar sendo executado localmente. O formato de dados é o mesmo usado pelo ChatGPT, então um histórico local anterior pode ser sincronizado sem conversão.

Exemplo de validação local, se desejado:

```bash
python3 .agents/skills/icarus-coaching/scripts/icarus_tracker.py validate
```

## Exemplos de uso

- “Icarus, qual é o treino de hoje?”
- “Começa o treino.”
- “Supino: 80 kg, 8 reps, 2 RIR.”
- “Corrige a última: eram 82,5 kg.”
- “Terminei. RPE 8, 60 minutos.”
- “Como evoluí no supino?”
- “Audite meu treino e descubra o principal gargalo.”
- “O que o corpus diz sobre volume para naturais e o que a ciência atual diz?”

Também é possível invocar explicitamente `$icarus-coaching`, `$icarus-evidence` ou `$icarus-corpus` quando o ambiente oferecer esse mecanismo.
