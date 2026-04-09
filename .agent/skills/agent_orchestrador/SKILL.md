---
name: agent_orchestrador
description: Orquestrar o fluxo completo de agentes de compras com controle de carga, incluindo inicialização, execução e finalização de discovery, trust_analysis e ranking. Usar quando for necessário evitar sobrecarga do sistema, limitar concorrência, processar ofertas em lotes e garantir encerramento limpo de cada etapa mesmo em caso de erro.
---

# Executar Fluxo Orquestrado

1. Validar a entrada do usuário.
2. Enfileirar a solicitação para respeitar limite de workflows concorrentes.
3. Iniciar o workflow somente após obter slot de execução.
4. Executar `product_discovery`.
5. Limitar quantidade de ofertas antes de iniciar `trust_analysis`.
6. Executar `trust_analysis` com concorrência controlada.
7. Executar `ranking` apenas com ofertas aprovadas.
8. Finalizar o workflow em bloco `finally`, removendo estado ativo mesmo após falhas.

# Aplicar Regras de Carga

- Limitar workflows simultâneos do orquestrador.
- Limitar ofertas enviadas para validação de confiança.
- Limitar concorrência interna das validações por loja.
- Definir timeout por validação externa.
- Continuar o fluxo quando uma validação individual falhar.

# Controlar Ciclo de Vida dos Agentes

- Iniciar agente somente no momento da etapa correspondente.
- Impedir execução de `ranking` sem `trust_analysis` concluído.
- Encerrar etapa atual antes de avançar para a próxima.
- Registrar logs de início e fim por `workflow_id`.
- Liberar recursos e estado ativo ao finalizar.

# Priorizar Robustez Operacional

- Tratar lista vazia após cada etapa como saída válida.
- Evitar falha global por erro pontual de loja.
- Selecionar subconjunto de ofertas para reduzir custo sob alta demanda.
