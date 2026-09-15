# Protocolo de treino ao vivo

Use este fluxo quando o usuário estiver na academia, perguntar pelo treino do dia, ditar séries ou pedir evolução.

## Invariantes

- `training/data/` é a memória persistente; a conversa pode manter somente um buffer transitório da sessão atual.
- No início, carregue do repositório o programa, a sessão aplicável e o histórico comparável necessário para conduzir o treino.
- Durante a sessão, não releia nem grave o GitHub a cada série. Acumule os eventos da sessão no buffer transitório.
- Consulte novamente o repositório no meio do treino somente quando faltar contexto persistente relevante, houver ambiguidade dependente do histórico, suspeita de alteração concorrente ou pedido explícito de comparação adicional.
- Faça a persistência em lote ao finalizar, cancelar ou quando o usuário pedir explicitamente um checkpoint.
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

Execute semanticamente `today`. Carregue de uma vez o que for necessário para a sessão: programa ativo, rotação, eventual sessão ativa e histórico comparável dos exercícios do treino. Informe:

- sessão e objetivo;
- exercícios na ordem;
- alvos de séries, repetições, RIR e descanso;
- desempenho na última exposição e sugestão de progressão, se houver;
- qualquer sessão incompleta que precise continuar ou cancelar.

Não despeje análise longa antes do treino. Priorize o próximo passo.

## Início

Ao usuário confirmar que começou, execute semanticamente `start` no buffer da sessão. Prontidão, sono e peso são opcionais; não transforme o começo do treino em interrogatório. Se houver dor ou sintoma relevante, aplique `knowledge/SAFETY.md` antes de iniciar.

Gere `session_id`, `event_id` e `session_started` conforme o schema e mantenha-os no buffer transitório. Não é necessário criar ou atualizar o arquivo remoto nesse momento. Diga que a sessão está em andamento, mas reserve termos como “salvo” ou “persistido” para depois do flush bem-sucedido.

## Registro de série

Converta linguagem natural para `set_logged`. Resolva antes de aceitar no buffer quando houver ambiguidade material:

- “20 de cada lado” em barra: confirme se a barra entra no total e seu peso;
- halteres: registre `per_hand`, não some os dois;
- máquina: mantenha o mesmo `exercise_id` apenas na mesma máquina/configuração comparável;
- peso corporal ou assistência: use o contexto correto;
- decimal brasileiro: `77,5` significa `77.5`.

Depois de aceitar uma série no buffer, responda em no máximo três blocos curtos:

1. confirmação exata da série entendida, deixando claro apenas quando necessário que a persistência remota ocorrerá no encerramento;
2. comparação relevante com o histórico já carregado;
3. orientação para a próxima série, sem alterar o programa por impulso.

Não faça round-trip ao GitHub por série. Se a comparação pedida exigir um histórico que não foi carregado no início, consulte o repositório pontualmente.

Se o usuário corrigir um dado, não apague o evento anterior. Acrescente ao buffer `set_corrected` com `replaces_event_id` apontando para o evento substituído. Se não estiver claro qual série deve ser corrigida, esclareça antes de criar a correção.

## Checkpoint opcional

Se o usuário pedir explicitamente para salvar o progresso antes do fim, faça um flush dos eventos pendentes para o log remoto usando `github-memory.md`. Depois do sucesso, mantenha a sessão ativa e continue acumulando apenas os eventos novos no buffer.

## Encerramento

Execute semanticamente `finish` apenas quando o usuário disser que terminou. Acrescente `session_completed` ao buffer e então faça um único flush seguro de todos os eventos pendentes para o log da sessão, quando possível.

Só depois do sucesso remoto diga que o treino foi finalizado/salvo. Em seguida, entregue resumo breve, PRs comparáveis, evolução ou queda relevante e a próxima sessão da rotação. Não diagnostique fadiga com uma única sessão.

Use `session_cancelled` para treino abandonado; registre motivo sem julgamento, faça o flush em lote e não avance a rotação.

## Evolução

Execute semanticamente `progress`. Fora de uma sessão ao vivo ou quando a pergunta exigir dados além do snapshot carregado, consulte o estado persistente atual. Interprete:

- tendência de e1RM junto com RIR;
- carga/repetições no mesmo padrão;
- volume externo por exposição;
- dor, notas, prontidão e aderência;
- ao menos três exposições antes de chamar algo de platô, salvo regressão abrupta ou segurança.

PR de máquina ou halter vale apenas para o mesmo ID e contexto de carga.
