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

## Regras gerais

- Releia o arquivo imediatamente antes de qualquer atualização.
- Para atualizar arquivo existente, use sempre o SHA da leitura mais recente.
- Se a escrita falhar por conflito ou SHA desatualizado, releia, reconcilie sem perder eventos existentes e tente novamente.
- Nunca substitua um JSONL por uma versão que remova linhas já persistidas.
- Uma resposta da ferramenta de escrita com sucesso é a confirmação de persistência.
- Não diga “registrado”, “salvo”, “corrigido”, “iniciado” ou “finalizado” antes desse sucesso.
- Escreva dados de treino diretamente em `main`; não crie PR ou branch temporária para eventos de uma sessão ao vivo.
- O repo é privado e foi explicitamente autorizado pelo proprietário para conter `training/data/`. Não replique esses dados em outro serviço.

## Inicialização

Quando `training/data/profile.json` ou `training/data/active_program.json` não existirem:

1. leia os templates em `training/templates/`;
2. faça o onboarding;
3. crie os arquivos reais somente com os dados confirmados;
4. valide conforme `training/SCHEMA.md`;
5. marque `onboarding_complete=true` e `status=active` apenas após a validação lógica.

Não crie defaults e os trate como perfil real sem confirmação.

## Carregamento do estado

Para executar `today`, `start`, `log-set`, `correct-last-set`, `finish`, `cancel`, `progress` ou `validate`:

1. leia `profile.json` e `active_program.json`;
2. liste `training/data/logs/` recursivamente por ano e mês;
3. leia os arquivos `.jsonl` necessários;
4. parseie os eventos em ordem de `timestamp`; em empate, preserve a ordem das linhas;
5. aplique `set_corrected`: eventos cujo `event_id` esteja em `replaces_event_id` de uma correção deixam de ser efetivos;
6. agrupe por `session_id`.

Uma sessão está ativa quando possui `session_started` e não possui `session_completed` nem `session_cancelled`.

Uma sessão conta para rotação somente quando possui `session_completed`. Sessão cancelada não avança.

## IDs e timestamps

- `schema_version`: `1`.
- `event_id`: UUID v4 único gerado para cada evento novo.
- `timestamp`: ISO 8601 com offset do fuso definido em `profile.athlete.timezone`; fallback `America/Sao_Paulo`.
- `session_id`: `<YYYY-MM-DD>-<session_key>-<6 caracteres hex únicos>`.

IDs novos são dados gerados pela operação; nunca reutilize um ID existente.

## `today`

1. valide perfil e programa;
2. detecte sessão ativa;
3. se houver sessão ativa, ela é o treino atual;
4. caso contrário, determine a próxima `session_key` pela rotação usando apenas sessões concluídas;
5. para cada exercício, encontre a exposição concluída mais recente com o mesmo `exercise_id`;
6. mostre alvo e `progression_hint` equivalente ao tracker.

Para double progression, se todas as séries-alvo da exposição anterior atingiram o topo da faixa de reps sem ficar abaixo do RIR mínimo, sugira o incremento configurado. Caso contrário, priorize adicionar repetição mantendo técnica e RIR.

## `start`

Antes de criar a sessão, confirme que não existe outra ativa.

Crie:

`training/data/logs/YYYY/MM/<session_id>.jsonl`

A primeira e única linha inicial deve ser um objeto `session_started` compatível com `training/SCHEMA.md`, incluindo `session_key`, `program_id`, prontidão/sono/peso/notas quando informados.

Crie o arquivo no GitHub e só então confirme que o treino começou.

## `log-set`

1. identifique a sessão ativa e seu arquivo;
2. resolva o exercício contra a definição da sessão;
3. valide carga, reps, RIR, dor, unidade e `load_context`;
4. calcule `set_number` a partir das séries efetivas já registradas daquele `exercise_id`, salvo número explícito;
5. crie `set_logged` conforme o schema;
6. releia o log e obtenha o SHA atual;
7. acrescente **uma nova linha JSON compacta ao final**, preservando todas as linhas anteriores e uma quebra de linha final;
8. atualize o arquivo usando o SHA atual;
9. após sucesso, compare com a exposição concluída anterior.

Mensagem de commit recomendada:

`training: log <exercise_id> set <N>`

Cada série deve ser persistida assim que for informada. Um commit por série é aceitável e preferível a perder estado de um treino ao vivo.

## `correct-last-set`

Nunca apague ou edite a linha original.

1. determine a série efetiva a corrigir;
2. copie os campos da série original;
3. aplique somente as alterações informadas;
4. gere novo `event_id` e `timestamp`;
5. use `type="set_corrected"`;
6. inclua `replaces_event_id=<event_id original>` e `correction_reason`;
7. anexe ao mesmo JSONL usando o protocolo seguro de SHA.

Mensagem de commit recomendada:

`training: correct <exercise_id> set <N>`

## `finish`

Somente quando o usuário disser que terminou:

1. identifique a sessão ativa;
2. crie `session_completed` com RPE, duração e notas quando informados;
3. anexe ao log com escrita segura;
4. após sucesso, a sessão torna-se imutável;
5. calcule resumo e próxima sessão da rotação.

Mensagem de commit recomendada:

`training: finish <session_id>`

## `cancel`

Anexe `session_cancelled` com motivo. Não avance a rotação.

Mensagem de commit recomendada:

`training: cancel <session_id>`

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
- no máximo uma sessão está ativa.

Se houver inconsistência, não escreva novos eventos até reconciliar o estado ou explicar o problema ao usuário.
