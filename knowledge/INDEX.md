# Roteador de conhecimento

Use apenas os arquivos necessários para a pergunta atual.

| Necessidade | Leia | Depois consulte |
|---|---|---|
| Tom, personalidade ou conteúdo em voz do Icarus | `PERSONA.md` | exemplos no catálogo, se necessário |
| Princípios gerais do método | `PRINCIPLES.md` | transcrições citadas |
| Montar ou adaptar um treino | `PROGRAM_DESIGN.md` | `PRINCIPLES.md` e `EXERCISE_SELECTION.md` |
| Treino do dia, registro ao vivo ou evolução | skill `$icarus-coaching` | `training/SCHEMA.md`, `references/live-workout.md` e o backend ativo (`references/notion-memory.md` no Claude; `references/github-memory.md` + `training/data/` no ChatGPT) |
| Escolher/substituir exercícios | `EXERCISE_SELECTION.md` | fontes por grupamento em `SOURCES.md` |
| Responder com ciência ou checar uma afirmação | `EVIDENCE.md` | fonte externa atual e transcrição relevante |
| Dor, doença, retorno ou população especial | `SAFETY.md` | fontes profissionais atuais |
| Localizar um vídeo/transcrição | `SOURCES.md` | arquivo original em `../icaro/` |
| Incorporar material novo | skill `$icarus-corpus` | `SOURCES.md` e síntese temática afetada |

## Regra de leitura

As sínteses são mapas, não substitutos das fontes. Para uma resposta que atribua uma ideia a Ícaro Lermen, confira a transcrição e o contexto das linhas indicadas. Para uma afirmação científica, use literatura externa atual; o corpus sozinho não basta.

## Convenções

- `Sxx`: transcrição primária.
- `Axx`: artefato derivado ou exemplo criado a partir do corpus.
- Referência interna: `[S12, l. 10–53]`.
- “Série válida”: série de trabalho suficientemente exigente para contar no volume; a definição operacional deve ser declarada quando a precisão importar.
- “Volume”: por padrão, número de séries válidas por músculo e por semana. Se usar tonelagem, repetições totais ou outro conceito, nomeie explicitamente.
