# Backend de memória no GitHub

Este é o backend canônico do Icarus quando executado no ChatGPT com acesso de leitura e escrita ao repositório privado `GuilhermeMendesRosa/icarus`.

A branch canônica é `main`.

## Princípio

O GitHub substitui o disco local como meio de persistência, mas **não altera o contrato dos dados**. Continue usando exatamente:

- `training/data/profile.json`;
- `training/data/active_program.json`;
- `training/data/logs/YYYY/MM/<session_id>.jsonl`;
- o schema de `training/SCHEMA.md`.

`scripts/icarus_tracker.py` é a implementação de referência para semântica, validações, rotação, comparação e métricas. No ChatGPT, reproduza essas operações diretamente por leitura e escrita no GitHub.

Para reduzir latência em treino ao vivo, o ChatGPT usa um **snapshot persistente carregado no início + buffer transitório de eventos da sessão**. O buffer existe somente para a sessão corrente e não substitui `training/data/` como memória entre conversas.

## Regras gerais

- Carregue no início da sessão tudo que provavelmente será necessário para conduzir o treino: perfil, programa, rotação, sessão aplicável e histórico comparável dos exercícios daquele treino.
- Não releia nem grave o GitHub a cada série.
- Durante a sessão, acumule os novos eventos no buffer transitório, com `event_id` e `timestamp` definidos quando o evento é criado.
- Consulte o GitHub novamente no meio da sessão somente quando faltar contexto persistente relevante, houver ambiguidade dependente do histórico, suspeita de concorrência ou pedido explícito de informação não carregada.
- Faça o flush dos eventos pendentes ao finalizar, cancelar ou quando o usuário pedir explicitamente um checkpoint.
- Antes de qualquer flush em arquivo existente, releia-o imediatamente e use o SHA mais recente.
- Nunca substitua um JSONL por uma versão que remova linhas já persistidas.
- Uma resposta da ferramenta de escrita com sucesso é a confirmação de persistência.
- Não diga “salvo”, “persistido”, “finalizado” ou equivalente antes desse sucesso. Durante o treino, pode confirmar que a série foi entendida/adicionada ao buffer.
- Escreva dados de treino diretamente em `main`; não crie PR ou branch temporária para eventos de uma sessão ao vivo.
- O repo é privado e foi explicitamente autorizado pelo proprietário para conter `training/data/`. Não replique esses dados em outro serviço.
- Campos opcionais só devem ser incluídos quando houver dado real para eles. Nunca transforme ausência de relato em valor presumido.

## Robustez operacional no ChatGPT

O objetivo é minimizar round-trips sem perder a segurança append-only:

- Descubra/carregue as ações GitHub necessárias uma vez no início da sessão ou quando o ambiente exigir.
- Gere cada `event_id` uma única vez quando o evento entra no buffer. Em retries do flush, preserve esses mesmos IDs.
- Em um flush, releia o log remoto se ele já existir e indexe seus `event_id`.
- Para cada evento pendente, anexe somente os IDs que ainda não estiverem persistidos.
- Preserve integralmente todas as linhas remotas já existentes, inclusive eventos que tenham surgido por outra conversa ou checkpoint.
- Quando não houver arquivo remoto para a sessão, crie-o contendo todos os eventos pendentes em ordem lógica.
- Quando houver arquivo remoto, faça uma única atualização com todos os eventos pendentes ausentes, sempre que possível.
- Se houver conflito de SHA, releia, reconcilie novamente por `event_id` e tente o flush com o mesmo conjunto de IDs.
- Se a resposta da escrita tiver status incerto, releia primeiro. Se todos os `event_id` pretendidos estiverem presentes, trate o flush como concluído; caso contrário, anexe apenas os ausentes.
- Nunca altere silenciosamente carga, reps, RIR, `set_type`, `exercise_id`, timestamps ou outros dados só para fazer um retry passar.

Esse protocolo torna o **flush da sessão** idempotente: uma nova tentativa não pode duplicar eventos já persistidos.

## Inicialização

Quando `training/data/profile.json` ou `training/data/active_program.json` não existirem:

1. leia os templates em `training/templates/`;
2. faça o onboarding;
3. crie os arquivos reais somente com os dados confirmados;
4. valide conforme `training/SCHEMA.md`;
5. marque `onboarding_complete=true` e `status=active` apenas após a validação lógica.

Não crie defaults e os trate como perfil real sem confirmação.

## Carregamento do estado

### Início de sessão / `today`

Para `today` ou início do parceiro ao vivo:

1. leia `profile.json` e `active_program.json`;
2. determine a rotação e a sessão aplicável usando somente sessões concluídas persistidas;
3. detecte eventual sessão remota ativa;
4. leia os logs necessários para encontrar a exposição concluída mais recente e o histórico comparável dos exercícios da sessão atual;
5. parseie os eventos em ordem de `timestamp`; em empate, preserve a ordem das linhas;
6. aplique `set_corrected`: eventos cujo `event_id` esteja em `replaces_event_id` de uma correção deixam de ser efetivos;
7. mantenha esse estado como snapshot para orientar o restante do treino.

Não faça uma nova carga completa antes de cada `log-set`.

### Consultas adicionais durante a sessão

Leia novamente somente o subconjunto necessário quando:

- o usuário pedir evolução/histórico que não foi carregado no snapshot;
- surgir dúvida sobre sessão ou exercício que dependa de dado persistente não disponível;
- houver indicação de que outra conversa/processo alterou o mesmo treino;
- for iniciar um flush/checkpoint.

## Estado de sessão

Uma sessão persistida está ativa quando possui `session_started` e não possui `session_completed` nem `session_cancelled`.

Durante uma sessão ainda não descarregada, o buffer transitório também representa uma sessão ativa para aquela conversa. Esse estado transitório não deve ser tratado como memória persistente em outra conversa.

Uma sessão conta para rotação somente quando `session_completed` estiver persistido. Sessão cancelada não avança.

## IDs e timestamps

- `schema_version`: `1`.
- `event_id`: UUID v4 único gerado para cada evento novo.
- `timestamp`: ISO 8601 com offset do fuso definido em `profile.athlete.timezone`; fallback `America/Sao_Paulo`.
- `session_id`: `<YYYY-MM-DD>-<session_key>-<6 caracteres hex únicos>`.

IDs novos são dados gerados pela operação; nunca reutilize um ID de outra operação. Em retries do mesmo flush, preserve os IDs já gerados.

## `today`

1. valide perfil e programa;
2. detecte sessão persistida ativa;
3. se houver sessão persistida ativa, ela é o treino atual;
4. caso contrário, determine a próxima `session_key` pela rotação usando apenas sessões concluídas;
5. para cada exercício do treino, encontre a exposição concluída mais recente com o mesmo `exercise_id` e carregue contexto comparável útil;
6. mostre alvo e `progression_hint` equivalente ao tracker.

Para double progression, se todas as séries-alvo da exposição anterior atingiram o topo da faixa de reps sem ficar abaixo do RIR mínimo, sugira o incremento configurado. Caso contrário, priorize adicionar repetição mantendo técnica e RIR.

## `start`

Antes de iniciar no buffer, confirme pelo snapshot que não existe outra sessão persistida ativa incompatível.

Gere uma vez:

- `session_id`;
- `event_id`;
- evento `session_started` compatível com `training/SCHEMA.md`.

Inclua prontidão/sono/peso/notas somente quando informados. Mantenha o evento no buffer; não é necessário criar o arquivo remoto ainda.

## `log-set`

1. identifique a sessão corrente no buffer;
2. resolva o exercício contra a definição da sessão;
3. valide carga, reps, RIR, dor, unidade e `load_context`;
4. calcule `set_number` a partir das séries efetivas persistidas no snapshot + eventos efetivos do buffer daquele `exercise_id`, salvo número explícito;
5. crie `set_logged` conforme o schema, incluindo apenas campos opcionais realmente informados;
6. gere `event_id` único e `timestamp` no momento do relato;
7. acrescente o evento ao buffer, sem escrita remota;
8. compare com o histórico comparável já carregado; busque contexto adicional no GitHub apenas se realmente necessário.

## `correct-last-set`

Nunca apague ou edite o evento original.

1. determine a série efetiva a corrigir no snapshot + buffer;
2. copie os campos da série original;
3. aplique somente as alterações informadas;
4. gere novo `event_id` e `timestamp`;
5. use `type="set_corrected"`;
6. inclua `replaces_event_id=<event_id original>` e `correction_reason`;
7. acrescente a correção ao buffer; ela será persistida no próximo flush.

## Checkpoint

Quando o usuário pedir explicitamente para salvar antes do fim:

1. faça o flush de todos os eventos pendentes;
2. depois do sucesso, marque esses eventos como persistidos no estado transitório;
3. mantenha a sessão aberta;
4. continue bufferizando apenas os novos eventos.

## `finish`

Somente quando o usuário disser que terminou:

1. crie `session_completed` com RPE, duração e notas somente quando informados;
2. acrescente-o ao buffer;
3. faça o flush de todos os eventos pendentes em uma única criação/atualização remota quando possível;
4. após sucesso confirmado, a sessão torna-se persistida e imutável;
5. calcule resumo e próxima sessão da rotação.

Mensagem de commit recomendada:

`training: finish <session_id>`

## `cancel`

Acrescente `session_cancelled` com motivo quando informado e faça o flush em lote. Não avance a rotação.

Mensagem de commit recomendada:

`training: cancel <session_id>`

## Algoritmo de flush

Para uma sessão em `training/data/logs/YYYY/MM/<session_id>.jsonl`:

1. ordene os eventos pendentes pela ordem em que foram gerados;
2. procure o arquivo remoto da sessão;
3. se não existir, crie-o com todos os eventos pendentes, uma linha JSON compacta por evento e quebra de linha final;
4. se existir, releia o conteúdo e SHA atual imediatamente antes da escrita;
5. extraia os `event_id` já persistidos;
6. descarte do lote somente os eventos cujos IDs já estejam presentes;
7. se não restar nenhum evento, considere o flush resolvido sem nova escrita;
8. caso contrário, acrescente todas as linhas ausentes ao final, preserve integralmente o conteúdo existente e faça **uma** atualização com o SHA atual;
9. em conflito ou resultado incerto, releia e repita a reconciliação por `event_id` antes de nova tentativa.

## Comparabilidade

Compare somente eventos com o mesmo:

- `exercise_id`;
- `unit`;
- `load_context`.

Considere também técnica, amplitude, dor, RIR e equipamento antes de declarar melhora.

Para halteres, `per_hand` significa a carga de um único halter. Não some as mãos.

Para máquina, mudança relevante de máquina/configuração requer novo `exercise_id`.

## e1RM

Reproduza a referência do tracker:

`e1RM = peso × (1 + (reps + RIR) / 30)`

Use apenas quando:

- `load_context` não for `bodyweight`, `assisted` ou `other`;
- peso for positivo;
- reps estiver entre 1 e 20;
- RIR, quando usado, estiver entre 0 e 5.

É uma estimativa de tendência, não teste máximo.

## Volume externo

Para séries em contextos compatíveis com carga externa:

`volume = peso × reps`

Não trate tonelagem como medida direta de hipertrofia.

## PR e platô

Só declare PR quando o histórico comparável sustentar melhora de carga, reps ou e1RM.

Não chame uma sessão ruim de platô. Em geral, exija pelo menos três exposições comparáveis antes de concluir estagnação.

## Validação remota

Antes de ativar programa ou após alteração estrutural, confira pelo menos:

- `schema_version == 1` em perfil, programa e eventos;
- rotação é lista e aponta apenas para sessões existentes;
- cada sessão possui exercícios;
- `exercise_id` é único dentro da sessão;
- cada exercício tem nome, `target_sets`, `rep_range`, `target_rir`, `rest_seconds` e `load_context` válido;
- `event_id` não se repete;
- cada `set_corrected.replaces_event_id` aponta para evento anterior da mesma sessão;
- campos opcionais ausentes não foram materializados como valores presumidos;
- no máximo uma sessão persistida está ativa.

Se houver inconsistência material, não faça flush até reconciliar o estado ou explicar o problema ao usuário.
