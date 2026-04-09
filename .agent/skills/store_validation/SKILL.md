---
name: store_validation
description: Validar confianca de lojas encontradas em buscas de produto e bloquear ofertas de alto risco. Usar quando o pipeline retornar lojas e for necessario justificar confiabilidade com metricas objetivas (reputacao, atendimento, seguranca de dominio e sinais de risco).
---

# Objetivo
Garantir que somente ofertas de lojas confiaveis avancem no ranking final.

# Fluxo Obrigatorio
1. Receber uma lista de ofertas com `store` e `url`.
2. Normalizar o nome da loja para comparar com base conhecida.
3. Calcular metricas de reputacao:
   - `reclame_aqui_rating` (0 a 10)
   - `trustpilot_rating` (0 a 5)
   - `response_rate` (0 a 1)
   - `resolution_rate` (0 a 1)
   - `years_online` (anos)
4. Calcular metricas de seguranca:
   - `https_score` (1 para HTTPS, 0 para HTTP)
   - `domain_match_score` (0 a 1, dominio oficial x dominio da oferta)
   - `domain_reputation_score` (0 a 1, penalizar TLD suspeito)
5. Produzir score final ponderado:
   - `reputation_score = 45% RA + 15% Trustpilot + 20% response + 20% resolution`
   - `operational_score = 35% response + 45% resolution + 20% years_online_score`
   - `trust_score = 55% reputation + 25% operational + 20% security`
6. Aprovar loja apenas se:
   - `trust_score >= 0.65`
   - `response_rate >= 0.65`
   - `resolution_rate >= 0.65`
   - `security_score >= 0.55`
7. Anexar explicacao objetiva com:
   - score final
   - principais metricas
   - riscos detectados (`risk_flags`)
   - resumo textual (`review_summary`)

# Regras de Saida
- Retornar `integrity_verified=true` apenas para lojas aprovadas.
- Preencher `trust_metrics` com os dados brutos usados no score.
- Preencher `trust_reasons` com justificativas humanas e auditaveis.
- Definir `trust_label` em `alta`, `moderada` ou `baixa`.

# Regras de Risco
- Marcar risco quando dominio nao combinar com loja esperada.
- Marcar risco quando TLD for suspeito (`.click`, `.xyz`, `.top`, `.gq`, `.support`, `.work`).
- Marcar risco quando resposta/resolucao de reclamacoes estiver abaixo do limite.
- Marcar risco quando score final ficar abaixo do limite de aprovacao.

# Arquivos-Alvo neste projeto
- `shopping_assistant/tools/store_validator.py`: motor de validacao e calculo de metricas.
- `shopping_assistant/agents/trust_analysis.py`: aplicacao do motor e filtro de ofertas aprovadas.
- `shopping_assistant/schemas/product.py`: campos de explicabilidade (`trust_label`, `trust_reasons`, `trust_metrics`).

# Checklist de Validacao
1. Rodar consulta comum (`iphone 13`, `playstation 5`).
2. Confirmar que produtos aprovados possuem `integrity_verified=true`.
3. Confirmar que `trust_score`, `response_rate`, `resolution_rate` e `review_summary` estao preenchidos.
4. Confirmar que `trust_metrics` inclui pelo menos: RA, Trustpilot, security score e risk flags.
