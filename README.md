# Icarus

Icarus é um workspace do Codex para coaching de treino resistido baseado em ciência, com foco em praticantes naturais e com personalidade inspirada no conteúdo educacional de Ícaro Lermen. Além de montar programas, ele mantém um diário local para informar o treino do dia, registrar séries pelo celular e acompanhar progressão.

Ao abrir esta pasta como projeto no Codex, o arquivo `AGENTS.md` fornece a identidade e as regras permanentes. As skills em `.agents/skills/` são descobertas pelo assunto do pedido e carregam apenas o fluxo necessário. A base `knowledge/` roteia o agente para as transcrições certas em `icaro/`, sem colocar todo o corpus no contexto de uma vez.

Esse desenho segue a descoberta oficial do Codex: instruções de projeto vêm de `AGENTS.md`, enquanto skills locais do repositório ficam em `.agents/skills` e usam divulgação progressiva. Veja a documentação oficial sobre [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) e [skills](https://learn.chatgpt.com/docs/build-skills).

## Como usar

Abra `/Users/guilherme.mendesrosa/code/icarus` como projeto e inicie uma nova tarefa. Você pode pedir naturalmente:

- “Icarus, monte um treino para 4 dias, 60 minutos, com prioridade em costas.”
- “Audite meu treino e descubra por que parei de progredir no supino.”
- “O que o corpus diz sobre volume para naturais e o que a ciência atual diz?”
- “Tenho só 35 minutos por sessão; adapte esta divisão.”
- “Integre estas novas transcrições à base.”
- “Icarus, qual é o treino de hoje?”
- “Registra: supino, 80 kg, 8 repetições, 2 RIR.”
- “Como evoluí nos últimos cinco treinos de costas?”

Também é possível invocar uma skill explicitamente com `$icarus-coaching`, `$icarus-evidence` ou `$icarus-corpus`.

## Estrutura

```text
AGENTS.md                 identidade, comportamento e invariantes
knowledge/                sínteses, evidência, segurança e roteamento
icaro/                    transcrições originais e um artefato derivado
training/                 perfil, programa ativo, logs e métricas
.agents/skills/
  icarus-coaching/        criação, acompanhamento ao vivo e evolução
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

## Treino pelo celular

O fluxo recomendado é o Codex Remote no ChatGPT mobile conectado ao computador onde este projeto está salvo. O trabalho é executado nesse computador, então o diário local continua disponível entre tarefas no mesmo projeto. Mantenha o computador acordado e online. Veja [training/README.md](training/README.md) e a documentação oficial do [Codex Remote](https://learn.chatgpt.com/docs/remote).

### Projeto comum do ChatGPT (sem computador)

Se a prioridade é usar o Icarus pelo celular sem depender do computador, use a versão portátil em um Projeto comum do ChatGPT. Ela mantém a conversa, a base de coaching e resumos salvos no próprio Projeto, mas **não** inclui o diário local validado pelo tracker. Projetos sincronizam chats, arquivos e instruções entre dispositivos; veja a documentação oficial de [Projetos no ChatGPT](https://help.openai.com/pt-br/articles/10169521-projetos-no-chatgpt).

1. No ChatGPT, crie o projeto **Icarus — Treino**.
2. Abra [`exports/chatgpt/PROJECT_INSTRUCTIONS.md`](exports/chatgpt/PROJECT_INSTRUCTIONS.md), copie o bloco e cole em **Configurações do projeto → Instruções do projeto**.
3. Envie apenas [`exports/chatgpt/ICARUS_CONTEXT.md`](exports/chatgpt/ICARUS_CONTEXT.md) como arquivo de referência.
4. No primeiro chat, envie: `Icarus, quero fazer meu onboarding como parceiro de treino.`
5. Mantenha um chat contínuo para o diário. Ao final de cada sessão, peça o **Resumo para salvar** e salve a resposta como fonte do Projeto.

Não envie `training/data/`, que contém dados pessoais locais. Essa versão começa o histórico do zero e não deve declarar evolução com base em memória conversacional não confirmada. Para comparações confiáveis de carga e histórico append-only, continue usando o fluxo local do Codex.

Chats em ambiente cloud clonam o repositório e apresentam alterações como diff; por isso, não use cloud como diário principal sem integrar cada mudança de volta. Os detalhes estão na documentação oficial de [cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environment).

Os dados pessoais em `training/data/` são ignorados pelo Git por padrão. Para começar:

> Icarus, quero fazer meu onboarding como parceiro de treino.
