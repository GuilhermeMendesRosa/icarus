# Icarus

Icarus é um agente de coaching de treino resistido baseado em ciência, com foco em praticantes naturais e personalidade inspirada no conteúdo educacional de Ícaro Lermen.

O uso principal é pelo **ChatGPT conectado ao repositório privado `GuilhermeMendesRosa/icarus`**. O repositório contém as instruções do agente, a base de conhecimento e a memória persistente de treino.

## Como funciona

Ao iniciar uma conversa no Projeto Icarus, o agente consulta:

- `AGENTS.md` para identidade, comportamento e invariantes;
- `knowledge/INDEX.md` para roteamento;
- `.agents/skills/` para o fluxo aplicável;
- `training/data/` para perfil, programa ativo e histórico persistente.

O objetivo é que o ChatGPT aja como uma interface do agente definido no repositório, em vez de manter uma cópia separada das regras.

## Estrutura

```text
AGENTS.md                 identidade, comportamento e invariantes
knowledge/                sínteses, evidência, segurança e roteamento
icaro/                    transcrições originais e artefatos derivados
training/
  SCHEMA.md               contrato dos dados
  README.md               arquitetura da memória
  data/                   perfil, programa e logs persistentes privados
.agents/skills/
  icarus-coaching/        criação, acompanhamento ao vivo e evolução
  icarus-evidence/        perguntas conceituais e checagem científica
  icarus-corpus/          ingestão e manutenção das transcrições
exports/chatgpt/
  PROJECT_INSTRUCTIONS.md bootstrap para o Projeto do ChatGPT
```

## Configuração recomendada no ChatGPT

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

A memória canônica fica em `training/data/`:

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
