# Esquema de dados

Versão atual: `1`.

## Perfil

`training/data/profile.json` contém:

- `onboarding_complete`: libera o uso operacional;
- `athlete`: nome preferido, fuso, unidade e peso corporal opcional;
- `goals`: objetivo principal, prioridades e horizonte;
- `availability`: frequência, duração e dias preferidos;
- `experience`: nível, anos e padrões dominados;
- `constraints`: equipamento, exercícios evitados, dores/restrições e observações;
- `recovery_baseline`: sono e estresse habituais.

Não registre diagnóstico, documento, endereço ou informação clínica desnecessária.

## Programa ativo

`training/data/active_program.json` só é operacional quando:

- `status` é `active`;
- `rotation` contém ao menos uma `session_key`;
- cada chave existe em `sessions`;
- cada exercício tem `exercise_id` único dentro da sessão, nome, séries-alvo, faixa de repetições, RIR, descanso e contexto de carga.

Exemplo de exercício:

```json
{
  "exercise_id": "supino-reto-barra",
  "name": "Supino reto com barra",
  "target_sets": 3,
  "rep_range": [6, 10],
  "target_rir": [1, 2],
  "rest_seconds": 180,
  "load_context": "total",
  "progression": {
    "type": "double_progression",
    "increment_kg": 2.5
  },
  "notes": "Mesma barra e mesma amplitude em todas as exposições."
}
```

`load_context` aceita:

- `total`: carga total externa;
- `per_hand`: carga informada por halter/mão;
- `machine_stack`: número exibido na mesma máquina;
- `bodyweight`: peso corporal sem carga externa;
- `assisted`: assistência; números menores podem representar progressão;
- `other`: comparação exige cautela.

Trocar de máquina, variante relevante, amplitude padronizada ou forma de contabilizar carga exige novo `exercise_id`.

## Eventos

Cada treino tem um arquivo `training/data/logs/YYYY/MM/<session_id>.jsonl`. Uma linha é um objeto JSON com `schema_version`, `event_id`, `timestamp`, `type` e `session_id`.

Tipos da versão 1:

- `session_started`: sessão, prontidão, sono, peso corporal e notas;
- `set_logged`: exercício, número da série, tipo, peso, unidade, repetições, RIR, dor, contexto e notas;
- `set_corrected`: cópia corrigida de uma série com `replaces_event_id`; métricas ignoram o evento substituído;
- `session_completed`: RPE, duração e notas finais;
- `session_cancelled`: motivo; não avança a rotação.

## Comparabilidade e métricas

Compare séries apenas com o mesmo `exercise_id`, unidade e `load_context`.

- **Carga:** peso externo informado.
- **Repetições:** repetições concluídas no padrão estabelecido.
- **Volume externo:** `peso × repetições`; não é medida direta de hipertrofia.
- **e1RM:** estimativa de Epley usando `repetições + RIR` quando RIR existe. É tendência, não teste máximo.
- **PR:** só declare quando o histórico comparável sustenta peso, repetições ou e1RM superior.

RIR, técnica, amplitude, dor e mudança de equipamento qualificam qualquer conclusão. Uma sessão isolada não justifica reprogramação automática.
