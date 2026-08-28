---
name: icarus-corpus
description: Incorpora, cataloga e sintetiza novas transcrições de Ícaro Lermen na base do Icarus. Use quando arquivos novos forem adicionados, quando o catálogo estiver desatualizado ou quando princípios/fontes precisarem de manutenção; não use para responder uma dúvida comum de treino.
---

# Icarus Corpus

Mantenha a base rastreável sem reescrever nem “limpar” as fontes originais.

## Fluxo

1. Leia [references/ingestion.md](references/ingestion.md).
2. Liste os arquivos novos e compare com `knowledge/SOURCES.md`.
3. Inspecione cada fonte no contexto. Separe conteúdo educacional, publicidade, conversa, demonstração e erro provável de ASR.
4. Registre um ID estável e tópicos no catálogo.
5. Atualize somente as sínteses realmente afetadas. Cada princípio atribuído deve apontar para ID e linhas.
6. Não promova uma alegação isolada ou ambígua a princípio central.
7. Execute `python3 .agents/skills/icarus-corpus/scripts/audit_catalog.py`.
8. Informe fontes adicionadas, sínteses alteradas e ambiguidades que ficaram abertas.

## Restrições

- Preserve arquivos em `icaro/` byte a byte, salvo pedido explícito para corrigir ou normalizar.
- Não renumere IDs existentes.
- Classifique conteúdo derivado como `Axx`, não `Sxx`.
- Não trate frequência de repetição como validação científica.
- Não copie longos trechos; sintetize e mantenha ponte para a fonte.
