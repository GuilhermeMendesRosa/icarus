# Backend de memória no Notion

Este é o backend canônico do Icarus quando executado no **Projeto do Claude (claude.ai, web, desktop ou celular)** com o conector do Notion ligado. As instruções e o conhecimento chegam pelo sync do GitHub (somente leitura); os dados de treino são lidos e gravados no Notion.

Desde 2026-10-06, o Notion é a fonte persistente de verdade para perfil, programa e histórico. `training/data/` no Git é um arquivo histórico congelado nessa data: não grave nele pelo Claude e não o trate como estado atual.

## Princípio

O Notion substitui o JSONL como meio de persistência, mas **não altera o contrato dos dados** de `training/SCHEMA.md`: mesmos `event_id`, `session_id`, `exercise_id`, `load_context`, tipos de evento, append-only, correções por `replaces_event_id`, comparabilidade e métricas. `scripts/icarus_tracker.py` continua sendo a implementação de referência da semântica (rotação, `progression_hint`, e1RM, PR); [github-memory.md](github-memory.md) continua descrevendo comparabilidade, e1RM, volume e validação, que valem aqui igualmente.

## Onde estão os dados

Tudo fica sob a página `Segundo Cérebro → Icarus`:

| Conteúdo | Tipo | ID / data source |
|---|---|---|
| Página Icarus | página | `ac86a9b347c24d38b13646cfdc7b7119` |
| Perfil (`profile.json`) | página com bloco JSON | `3f19f9e2a59381efa63df03434bca935` |
| Programa ativo (topo de `active_program.json`) | página com bloco JSON | `3f19f9e2a59381ea9db8d0f7ac480e4d` |
| Prescrição (`sessions[].exercises[]`) | banco | `collection://06fafb64-acbc-49c0-b237-fd4a35fc9424` |
| Exercícios (catálogo por `exercise_id`) | banco | `collection://12aea3c9-c607-429c-b1b5-05674020ae50` |
| Sessões (um treino por linha) | banco | `collection://0140fe40-afbd-40b8-ae02-6ffa843448ea` |
| Séries (`set_logged` / `set_corrected`) | banco | `collection://a7a8b944-17e7-4182-8020-40c9f3b6e0e9` |

Se um ID falhar, procure "Icarus" no Notion, reabra a página e localize os bancos pelo nome; não crie bancos novos por conta própria.

## Mapeamento evento → Notion

- `session_started` → nova linha em **Sessões**: `session_id` (título), `Data` (data local), `session_key`, `program_id`, `Status = ativa`, `Início` (timestamp), `start_event_id`, e somente quando informados `Prontidão` (`readiness_1_to_10`), `Sono (h)` (`sleep_hours`), `Peso corporal (kg)` (`bodyweight_kg`), `Notas início`.
- `session_completed` → atualiza a mesma linha: `Status = concluída`, `Fim`, `end_event_id`, e quando informados `RPE` (`session_rpe_1_to_10`), `Duração (min)` (`duration_minutes`), `Notas fim`.
- `session_cancelled` → `Status = cancelada`, `Fim`, `end_event_id`, `Motivo cancelamento` (`reason`).
- `set_logged` / `set_corrected` → nova linha em **Séries**: `event_id`, `Tipo`, `Sessão` (relação) + `session_id`, `Exercício` (relação ao catálogo) + `exercise_id`, `set_number`, `set_type`, `Peso`, `Unidade`, `Reps`, `RIR`, `load_context`, `Dor (0-10)` (`pain_0_to_10`), `Notas`, `Timestamp`, `Ordem` (posição do evento na sessão; `session_started` é 1) e, em correções, `replaces_event_id` e `correction_reason`.
- Título da série: `<exercise_id> · <peso> <unidade> × <reps> @ RIR <rir> (<set_type>)`, com ` [correção]` em `set_corrected`. É só legibilidade; o dado está nas propriedades.

Campos opcionais sem relato ficam **vazios**. Nunca preencha 0 ou valor presumido.

As linhas de **Séries** são append-only: nunca edite nem arquive uma linha já gravada. A linha da **Sessão** é o único registro que muda, e só nas transições `ativa → concluída` ou `ativa → cancelada`. Depois disso ela é imutável.

Um `exercise_id` novo (troca de máquina, variante ou forma de contar carga) exige primeiro criar a linha no catálogo **Exercícios** e só depois relacionar séries a ele.

## Consultas

O plano atual do Notion limita o modo SQL e não permite consulta multi-banco. Use `query-data-sources` em **modo `rows`** com filtro estruturado (até 100 linhas por chamada) e, para páginas, `fetch`. Reserve SQL para auditorias pontuais.

Consultas típicas:

- **Programa:** `fetch` em Programa ativo + Prescrição filtrada por `Ativo = true` (ordenar por `Sessão`, `Ordem`).
- **Rotação e sessão ativa:** Sessões ordenadas por `Data` desc, `limit` ~10. Sessão ativa = `Status = ativa`. A próxima `session_key` sai da rotação usando somente sessões `concluída` do programa ativo, como faz o tracker.
- **Histórico comparável:** Séries filtradas por `exercise_id` (texto) igual ao exercício, ordenadas por `Timestamp` desc. Agrupe por `session_id` para obter exposições.
- **Dedupe no flush:** Séries filtradas por `session_id` da sessão corrente, para coletar `event_id` já gravados.

Ao aplicar correções: um `event_id` presente em `replaces_event_id` de outra linha deixa de ser efetivo.

## Fluxo ao vivo

Igual ao do GitHub: snapshot no início, **buffer transitório** durante a sessão, persistência em lote.

1. `today`/início: carregue perfil, programa, prescrição da sessão aplicável, sessões recentes e histórico comparável dos exercícios do dia. Não releia a cada série.
2. `start`: gere `session_id` (`<YYYY-MM-DD>-<session_key>-<6 hex>`) e `event_id` (UUID v4) uma única vez e mantenha `session_started` no buffer.
3. `log-set` / `correct-last-set`: crie o evento no buffer com `event_id` e `timestamp` (ISO 8601 com offset de `profile.athlete.timezone`) no momento do relato.
4. Consulte o Notion no meio do treino só quando faltar dado persistente necessário, houver ambiguidade dependente do histórico ou o usuário pedir.

Durante a sessão, pode confirmar que a série foi entendida e adicionada ao buffer, mas não diga "salvo".

## Flush (finish, cancel ou checkpoint)

1. Releia **Séries** filtrando pelo `session_id` corrente e indexe os `event_id` já gravados. Releia a linha da sessão em **Sessões**, se existir.
2. Se a linha da sessão não existir, crie-a com os campos de `session_started` (`Status = ativa`).
3. Crie, em **uma** chamada `create-pages` (até 100 páginas), as séries pendentes cujo `event_id` ainda não está gravado, em ordem de geração e com `Ordem` sequencial.
4. Em `finish`/`cancel`, atualize a linha da sessão para `concluída`/`cancelada` com os campos de encerramento. Só faça isso **depois** que as séries tiverem sido gravadas.
5. Se a gravação retornar como assíncrona ou incerta, aguarde o término e releia Séries pelo `session_id`: os `event_id` presentes estão persistidos. Grave apenas os ausentes, com os **mesmos** IDs e valores. Nunca altere carga, reps, RIR, tipo ou timestamp para fazer uma nova tentativa passar.
6. Só depois de confirmar a presença de todos os `event_id` e o status final diga "salvo", "persistido" ou "finalizado". Então entregue o resumo e a próxima sessão da rotação.

Num checkpoint, mantenha `Status = ativa` e continue bufferizando apenas os eventos posteriores.

Esse protocolo deixa o flush idempotente por `event_id`: uma nova tentativa não duplica série já gravada.

## Onboarding e mudanças de programa

- Perfil: edite o bloco JSON da página Perfil inteiro, preservando o schema, e atualize o resumo.
- Novo programa: atualize a página Programa ativo (novo `program_id`) e, em Prescrição, desmarque `Ativo` das linhas antigas e crie as novas. Não apague linhas antigas; logs antigos continuam apontando para os `exercise_id` e o `program_id` com que foram gravados.
- Valide conforme a seção "Validação remota" de [github-memory.md](github-memory.md) antes de declarar o programa ativo.

## Honestidade operacional

Se o conector do Notion estiver desligado, sem permissão ou falhar, diga que não conseguiu ler ou gravar o estado. Pode continuar orientando o treino, mas deixe claro que os eventos ainda não foram persistidos, e mantenha-os no buffer para um flush posterior na mesma conversa.

Não copie esses dados para outro serviço sem pedido explícito.
