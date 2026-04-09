---
name: mongodb
description: Persistir e consultar dados operacionais no MongoDB para cache de validacao de lojas e trilha de eventos de orquestracao. Usar quando for necessario evitar revalidar a mesma loja/dominio, registrar hit/miss de cache, salvar resultados de trust analysis e auditar o fluxo completo do orquestrador.
---

# Configurar Conexao MongoDB

1. Definir `MONGODB_URI` com a string de conexao.
2. Definir `MONGODB_DATABASE` quando quiser nome de base diferente de `shopping_assistant`.
3. Definir `MONGODB_CACHE_COLLECTION` para alterar a colecao de cache.
4. Definir `MONGODB_EVENTS_COLLECTION` para alterar a colecao de eventos.
5. Definir `MONGODB_CACHE_TTL_HOURS` para controlar expiracao do cache.

# Aplicar Cache Antes da Validacao

1. Receber `store_name` e `product_url`.
2. Construir chave de cache com loja normalizada e dominio.
3. Consultar cache de validacao com filtro por `expires_at > now`.
4. Retornar resultado em caso de cache hit.
5. Executar validador apenas em caso de cache miss.
6. Persistir resultado novo no cache via upsert.

# Registrar Processo Completo

- Registrar evento de inicio do workflow.
- Registrar evento de inicio da trust analysis.
- Registrar evento `store_validation_cache_hit` por loja reutilizada.
- Registrar evento `store_validation_cache_miss` por loja revalidada.
- Registrar evento `store_validated_and_cached` apos validacao externa.
- Registrar evento `store_validation_failed` em erro pontual.
- Registrar evento de finalizacao da trust analysis.
- Registrar evento de finalizacao do workflow do orquestrador.

# Operar Com Resiliencia

- Continuar processamento quando MongoDB estiver indisponivel.
- Desativar cache automaticamente quando a inicializacao do cliente falhar.
- Evitar queda global por erro de persistencia de evento.

# Referencias

- Ler [references/mongodb_collections.md](references/mongodb_collections.md) para contratos de colecoes e indices.
