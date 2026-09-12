# Protocolo de treino ao vivo

Use este fluxo quando o usuário estiver na academia, perguntar pelo treino do dia, ditar séries ou pedir evolução.

## Invariantes

- `training/data/` é a memória; a conversa não é.
- Recarregue o estado persistente antes de responder sobre hoje ou evolução.
- Grave cada série assim que ela for informada e confirme somente após sucesso da escrita.
- Nunca invente peso, repetição, RIR, data ou sessão ausente.
- Treinos finalizados são imutáveis; correções são novos eventos append-only.
- Não avance a rotação em sessão cancelada.
- No ChatGPT, use `github-memory.md`; em ambiente local, o tracker pode ser usado.

## Onboarding

Se o estado indicar onboarding pendente:

1. leia `training/SCHEMA.md` e `knowledge/PROGRAM_DESIGN.md`;
2. colete apenas dados que mudam o programa;
3. preencha `training/data/profile.json` e `training/data/active_program.json` usando o backend persistente disponível;
4. use IDs estáveis e declare como a carga será contabilizada;
5. valide estruturalmente perfil e programa conforme `training/SCHEMA.md`;
6. só marque perfil completo e programa ativo quando não houver erro.

Não use o artefato A01 como programa ativo sem confirmação explícita do usuário.

## “Qual é o treino de hoje?”

Execute semanticamente `today`. Informe:

- sessão e objetivo;
- exercícios na ordem;
- alvos de séries, repetições, RIR e descanso;
- desempenho na última exposição e sugestão de progressão, se houver;
- qualquer sessão incompleta que precise continuar ou cancelar.

Não despeje análise longa antes do treino. Priorize o próximo passo.

## Início

Ao usuário confirmar que começou, execute semanticamente `start`. Prontidão, sono e peso são opcionais; não transforme o começo do treino em interrogatório. Se houver dor ou sintoma relevante, aplique `knowledge/SAFETY.md` antes de iniciar.

Crie um `session_started` no log da sessão e só diga que o treino foi iniciado depois de a persistência ter sucesso.

## Registro de série

Converta linguagem natural para `set_logged`. Resolva antes de gravar quando houver ambiguidade material:

- “20 de cada lado” em barra: confirme se a barra entra no total e seu peso;
- halteres: registre `per_hand`, não some os dois;
- máquina: mantenha o mesmo `exercise_id` apenas na mesma máquina/configuração comparável;
- peso corporal ou assistência: use o contexto correto;
- decimal brasileiro: `77,5` significa `77.5`.

Depois de registrar, responda em no máximo três blocos curtos:

1. confirmação exata;
2. comparação relevante com a exposição anterior;
3. orientação para a próxima série, sem alterar o programa por impulso.

Se o usuário corrigir um dado, não apague o evento anterior. Acrescente `set_corrected` com `replaces_event_id` apontando para o evento substituído. Confirme o valor efetivo depois do sucesso. Se não estiver claro qual série deve ser corrigida, esclareça antes de gravar.

## Encerramento

Execute semanticamente `finish` apenas quando o usuário disser que terminou. Grave `session_completed`, então entregue resumo breve, PRs comparáveis, evolução ou queda relevante e a próxima sessão da rotação. Não diagnostique fadiga com uma única sessão.

Use `session_cancelled` para treino abandonado; registre motivo sem julgamento e não avance a rotação.

## Evolução

Execute semanticamente `progress`, opcionalmente filtrando exercício. Interprete:

- tendência de e1RM junto com RIR;
- carga/repetições no mesmo padrão;
- volume externo por exposição;
- dor, notas, prontidão e aderência;
- ao menos três exposições antes de chamar algo de platô, salvo regressão abrupta ou segurança.

PR de máquina ou halter vale apenas para o mesmo ID e contexto de carga.
