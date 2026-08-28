---
name: icarus-evidence
description: Responde e verifica dúvidas sobre hipertrofia, força e treino natural comparando as transcrições de Ícaro Lermen com evidência científica atual. Use para perguntas conceituais, “o que a ciência diz”, checagem de afirmações e explicação de divergências; não use como fluxo principal para montar uma ficha completa.
---

# Icarus Evidence

Produza uma resposta útil para decisão, não uma revisão acadêmica automática.

## Fluxo

1. Leia `knowledge/EVIDENCE.md`.
2. Localize o tópico em `knowledge/SOURCES.md`, pesquise a transcrição com `rg -n -i` e leia o contexto.
3. Se o usuário pedir ciência, se a alegação for de saúde/lesão ou se precisão atual importar, pesquise literatura externa atual. Prefira revisão sistemática, meta-análise, consenso ou diretriz; avalie estudos primários quando necessário.
4. Separe claramente posição do corpus, ciência externa e inferência aplicada.
5. Informe confiança e a principal limitação quando elas mudarem a decisão.
6. Use [references/answer-shape.md](references/answer-shape.md) como formato flexível.

## Regras

- Não use a autoridade competitiva do autor como substituto de evidência.
- Não force o corpus a dizer mais do que a passagem sustenta.
- Não invente referências nem cite resultados a partir de snippets.
- Não confunda significância estatística com importância prática.
- Não transforme médias populacionais em limites universais.
- Se houver conflito, diga o que cada fonte sustenta e por que a recomendação final foi escolhida.
