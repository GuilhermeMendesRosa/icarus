# Protocolo de treino ao vivo

Use este fluxo quando o usuário estiver na academia, perguntar pelo treino do dia, ditar séries ou pedir evolução.

## Invariantes

- O disco é a memória; a conversa não é.
- Leia o estado com o CLI antes de responder sobre hoje ou evolução.
- Grave cada série assim que ela for informada e confirme somente após sucesso do comando.
- Nunca invente peso, repetição, RIR, data ou sessão ausente.
- Treinos finalizados são imutáveis; não edite JSONL manualmente.
- Não avance a rotação em sessão cancelada.

## Onboarding

Se `today` indicar onboarding pendente:

1. leia `training/SCHEMA.md` e `knowledge/PROGRAM_DESIGN.md`;
2. colete apenas dados que mudam o programa;
3. preencha `training/data/profile.json` e `training/data/active_program.json`;
4. use IDs estáveis e declare como a carga será contabilizada;
5. execute `validate`;
6. só marque perfil completo e programa ativo quando não houver erro.

Não use o artefato A01 como programa ativo sem confirmação explícita do usuário.

## “Qual é o treino de hoje?”

Execute `today`. Informe:

- sessão e objetivo;
- exercícios na ordem;
- alvos de séries, repetições, RIR e descanso;
- desempenho na última exposição e sugestão de progressão, se houver;
- qualquer sessão incompleta que precise continuar ou cancelar.

Não despeje análise longa antes do treino. Priorize o próximo passo.

## Início

Ao usuário confirmar que começou, execute `start`. Prontidão, sono e peso são opcionais; não transforme o começo do treino em interrogatório. Se houver dor ou sintoma relevante, aplique `knowledge/SAFETY.md` antes de iniciar.

## Registro de série

Converta linguagem natural para `log-set`. Resolva antes de gravar quando houver ambiguidade material:

- “20 de cada lado” em barra: confirme se a barra entra no total e seu peso;
- halteres: registre `per_hand`, não some os dois;
- máquina: mantenha o mesmo `exercise_id` apenas na mesma máquina/configuração comparável;
- peso corporal ou assistência: use o contexto correto;
- decimal brasileiro: `77,5` significa `77.5`.

Depois de registrar, responda em no máximo três blocos curtos:

1. confirmação exata;
2. comparação relevante com a exposição anterior;
3. orientação para a próxima série, sem alterar o programa por impulso.

Se o usuário corrigir um dado, não apague a linha. Execute `correct-last-set`, que acrescenta `set_corrected` apontando para o evento substituído. Confirme o valor efetivo depois do sucesso. Se não estiver claro qual série deve ser corrigida, esclareça antes de gravar.

## Encerramento

Execute `finish` apenas quando o usuário disser que terminou. Entregue resumo breve, PRs comparáveis, evolução ou queda relevante e a próxima sessão da rotação. Não diagnostique fadiga com uma única sessão.

Use `cancel` para treino abandonado; registre motivo sem julgamento.

## Evolução

Execute `progress`, opcionalmente filtrando exercício. Interprete:

- tendência de e1RM junto com RIR;
- carga/repetições no mesmo padrão;
- volume externo por exposição;
- dor, notas, prontidão e aderência;
- ao menos três exposições antes de chamar algo de platô, salvo regressão abrupta ou segurança.

PR de máquina ou halter vale apenas para o mesmo ID e contexto de carga.
