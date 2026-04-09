---
name: web_search
description: Implementar busca de produtos no Google Shopping e retornar ofertas estruturadas com nome, preço, loja e link. Usar quando o usuário pedir pesquisa de preço, comparação de ofertas ou busca de produto na aba Shopping do Google.
---

# Objetivo
Executar pesquisa real no Google com `tbm=shop` (aba Shopping) e converter o resultado para uma lista de ofertas utilizável pelos agentes.

# Fluxo Obrigatório
1. Normalizar a consulta do usuário (remover espaços extras e validar texto não vazio).
2. Fazer requisição HTTP para `https://www.google.com/search` com os parâmetros:
   - `q=<consulta>`
   - `tbm=shop`
   - `hl=pt-BR`
   - `gl=br`
   - `num=20`
3. Parsear HTML e extrair, para cada oferta:
   - `title`
   - `price`
   - `store`
   - `url`
4. Montar a resposta no schema `Product`.
5. Deduplicar por URL.
6. Aplicar fallback controlado se Google bloquear, mudar layout ou retornar vazio.

# Regras de Extração
- Preferir seletores de cards de Shopping: `div.sh-dgr__grid-result` e `div.sh-dlr__list-result`.
- Extrair preço em formato brasileiro (`R$ 1.999,90`) e converter para `float`.
- Resolver links relativos e links intermediários `/url?q=...` para URL final.
- Limitar em até 20 produtos por consulta.

# Regras de Robustez
- Definir `User-Agent` de navegador real e `Accept-Language` para `pt-BR`.
- Tratar timeout e erros de rede sem quebrar o fluxo.
- Se não houver resultados válidos, retornar ofertas fallback para manter continuidade do pipeline.

# Arquivos-alvo neste projeto
- `shopping_assistant/tools/search_api.py`: implementação da busca Google Shopping.
- `shopping_assistant/agents/product_discovery.py`: política de uso do scraper auxiliar.

# Formato de Saída Esperado
Retornar lista de objetos `Product` com:
- `title` (str)
- `price` (float)
- `store` (str)
- `url` (str)
- `source` (`google_shopping_live` ou `google_shopping_fallback`)

# Checklist de Validação
1. Executar busca com um produto comum (`iphone 13`, `playstation 5`, etc.).
2. Confirmar que há ao menos uma oferta com `price` numérico válido.
3. Confirmar que `url` é clicável e absoluta.
4. Confirmar que fluxo não quebra sem rede (fallback funcionando).
