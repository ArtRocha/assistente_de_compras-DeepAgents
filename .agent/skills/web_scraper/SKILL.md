---
name: web_scraper
description: Extrair ofertas de produto diretamente da pagina do Google Shopping e retornar dados estruturados com titulo, preco, loja e URL final. Usar quando a busca principal tiver baixa cobertura, quando for necessario ampliar recall com variacoes de consulta, ou quando o pipeline precisar de scraping live para complementar resultados da ferramenta web_search.
---

# Objetivo
Executar scraping live orientado a Google Shopping para aumentar cobertura de ofertas validas sem quebrar o pipeline quando houver mudanca de layout, bloqueio parcial ou baixa relevancia inicial.

# Fluxo Obrigatorio
1. Receber a consulta normalizada do usuario.
2. Gerar variacoes de consulta para ampliar cobertura sem fugir da intencao original.
3. Executar buscas em paralelo na aba Shopping (`tbm=shop`) para cada variacao.
4. Unificar resultados coletados e remover duplicatas.
5. Normalizar campos no schema `Product`.
6. Filtrar resultados por relevancia com comparacao fuzzy contra a consulta original.
7. Retornar lista final com ofertas prontas para trust analysis e ranking.

# Regras de Variacao de Query
- Manter a consulta original como primeira variacao.
- Adicionar variacoes com intencao comercial (`preco`, `comprar`) sem alterar modelo/produto.
- Remover prefixos comuns de ruido (ex.: `preco de`, `comprar`, `onde comprar`) para recuperar cards nao exibidos na primeira busca.
- Limitar a no maximo 4 variacoes por consulta para controlar custo e latencia.

# Regras de Extracao
- Priorizar parse de `application/ld+json` quando houver `itemListElement`.
- Aplicar fallback para parse por seletores de card quando JSON-LD estiver ausente.
- Extrair e validar obrigatoriamente: `title`, `price`, `store`, `url`.
- Resolver links intermediarios do Google (`/url?q=...`, `adurl`, `u`) para URL final da loja.
- Descartar links de pagina de busca e cards sem preco valido.
- Deduplicar por combinacao de `title + store + price`.
- Limitar retorno a 20 itens por rodada de parse consolidado.

# Regras de Robustez
- Executar buscas em paralelo e ignorar erro individual de uma variacao.
- Tratar timeout, erro HTTP e resposta vazia sem interromper o fluxo global.
- Inferir loja pelo dominio da URL quando o card nao informar vendedor.
- Manter `source` como `google_shopping_live`.

# Integracao no Projeto
- `shopping_assistant/tools/scraper.py`: orquestrar variacoes e consolidacao de resultados.
- `shopping_assistant/tools/search_api.py`: executar request em `tbm=shop` e parsear cards/JSON-LD.
- `shopping_assistant/agents/product_discovery.py`: acionar scraper como fallback quando cobertura da busca principal for baixa.

# Checklist de Validacao
1. Testar consulta comum (`iphone 13`, `playstation 5`, `air fryer`).
2. Confirmar retorno com `price` numerico (`float`) e `url` absoluta.
3. Confirmar deduplicacao e filtro fuzzy aplicados.
4. Confirmar resiliencia quando uma variacao falhar (pipeline continua).
5. Confirmar acionamento do scraper quando a busca principal retornar menos de 3 ofertas.
