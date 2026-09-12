# Memória de treino do Icarus

Esta pasta transforma o Icarus em um parceiro de treino persistente. O programa ativo define o que fazer; cada interação na academia gera um evento; os relatórios são calculados a partir do histórico, sem depender da memória da conversa.

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
.agents/skills/icarus-coaching/
  references/github-memory.md   backend oficial no ChatGPT
  scripts/icarus_tracker.py     implementação local/de referência
```

Os logs são append-only. Um treino finalizado não deve ser reescrito; correções entram como novos eventos `set_corrected`. `exercise_id` identifica uma combinação estável de exercício, máquina/implemento e forma de contabilizar a carga.

## Fonte canônica

O uso principal agora é pelo **ChatGPT conectado ao repositório privado `GuilhermeMendesRosa/icarus`**. A branch `main` é a fonte persistente canônica.

O proprietário autorizou explicitamente o versionamento de `training/data/` neste repositório privado para permitir continuidade entre conversas e dispositivos. Não torne o repositório público sem antes remover os dados pessoais e considerar a reescrita do histórico Git.

O ChatGPT deve usar `.agents/skills/icarus-coaching/references/github-memory.md` para ler e gravar o estado diretamente no GitHub. O `icarus_tracker.py` permanece útil como implementação de referência e para compatibilidade local, mas não é necessário para operar o Icarus no ChatGPT.

## Primeiro uso

Se `training/data/profile.json` e `training/data/active_program.json` ainda não existirem, peça:

> Icarus, quero fazer meu onboarding como parceiro de treino.

O agente deve coletar os dados mínimos, criar os dois arquivos no GitHub, validar logicamente o schema e só então ativar o programa.

Se já existe histórico local anterior, sincronize-o para `training/data/` preservando exatamente os arquivos atuais. O formato local e o remoto é o mesmo; não há migração de schema.

## Uso na academia

No Projeto Icarus do ChatGPT:

1. “Icarus, qual é o treino de hoje?”
2. “Começa o treino. Prontidão 8, dormi 7 horas.”
3. “Primeira do supino: 80 kg, 8 reps, 2 RIR.”
4. “Segunda: 80 por 7, 1 RIR.”
5. “Terminei. RPE da sessão 8, 64 minutos.”

Cada série inequívoca é persistida imediatamente no GitHub. A confirmação ao usuário só vem depois do sucesso da escrita.

## Operações canônicas

A semântica continua sendo:

- `today`: sessão atual/próxima e histórico relevante;
- `start`: cria `session_started`;
- `log-set`: acrescenta `set_logged`;
- `correct-last-set`: acrescenta `set_corrected`, sem apagar o original;
- `finish`: acrescenta `session_completed`;
- `cancel`: acrescenta `session_cancelled` sem avançar rotação;
- `progress`: calcula evolução apenas entre exposições comparáveis;
- `validate`: verifica integridade de perfil, programa e eventos.

No ChatGPT essas operações são executadas diretamente pelo backend GitHub. Localmente, os comandos equivalentes continuam disponíveis em `icarus_tracker.py`.

## Concorrência e segurança de escrita

Antes de atualizar um JSONL existente, o agente deve reler o arquivo e usar o SHA atual retornado pelo GitHub. Em conflito, deve reler e reconciliar, nunca sobrescrever linhas persistidas.

Treino finalizado é imutável. Uma sessão cancelada não avança a rotação.

## Privacidade

`training/data/` pode conter perfil, peso, desempenho, RIR, dor e notas pessoais. Esses dados estão versionados **somente porque o repositório é privado e o proprietário autorizou este uso**.

Não publique esses arquivos, não os copie para repositório público e não os mova para outro serviço sem pedido explícito.
