# Icarus

Icarus é um workspace do Codex para coaching de treino resistido baseado em ciência, com foco em praticantes naturais e com personalidade inspirada no conteúdo educacional de Ícaro Lermen.

Ao abrir esta pasta como projeto no Codex, o arquivo `AGENTS.md` fornece a identidade e as regras permanentes. As skills em `.agents/skills/` são descobertas pelo assunto do pedido e carregam apenas o fluxo necessário. A base `knowledge/` roteia o agente para as transcrições certas em `icaro/`, sem colocar todo o corpus no contexto de uma vez.

Esse desenho segue a descoberta oficial do Codex: instruções de projeto vêm de `AGENTS.md`, enquanto skills locais do repositório ficam em `.agents/skills` e usam divulgação progressiva. Veja a documentação oficial sobre [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) e [skills](https://learn.chatgpt.com/docs/build-skills).

## Como usar

Abra `/Users/guilherme.mendesrosa/code/icarus` como projeto e inicie uma nova tarefa. Você pode pedir naturalmente:

- “Icarus, monte um treino para 4 dias, 60 minutos, com prioridade em costas.”
- “Audite meu treino e descubra por que parei de progredir no supino.”
- “O que o corpus diz sobre volume para naturais e o que a ciência atual diz?”
- “Tenho só 35 minutos por sessão; adapte esta divisão.”
- “Integre estas novas transcrições à base.”

Também é possível invocar uma skill explicitamente com `$icarus-coaching`, `$icarus-evidence` ou `$icarus-corpus`.

## Estrutura

```text
AGENTS.md                 identidade, comportamento e invariantes
knowledge/                sínteses, evidência, segurança e roteamento
icaro/                    transcrições originais e um artefato derivado
.agents/skills/
  icarus-coaching/        criação, ajuste e auditoria de treino
  icarus-evidence/        perguntas conceituais e checagem científica
  icarus-corpus/          ingestão e manutenção das transcrições
```

## Validação

Da raiz do projeto:

```bash
python3 .agents/skills/icarus-corpus/scripts/audit_catalog.py
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/icarus-coaching
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/icarus-evidence
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/icarus-corpus
```

O Codex detecta alterações de skills automaticamente; se uma alteração não aparecer no seletor, reinicie a sessão.
