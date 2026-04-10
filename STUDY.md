# 🧠 Guia de Montagem: Integrando IA Real (Ollama) ao Projeto

Bem-vindo ao `STUDY.md`! Este documento foi criado para explicar didaticamente **o que foi feito**, **como foi feito** e **por que foi feito** durante a transformação do projeto de um sistema puramente lógico/determinístico para um verdadeiro sistema de Agentes Inteligentes.

Aqui usamos o **Ollama** para rodar modelos locais (como o `llama2`) de forma totalmente gratuita.

---

## 🏗️ 1. O Desafio Inicial

**Antes da mudança:**
O projeto já existia e funcionava muito bem, mas não tinha "Inteligência Artificial real".
- A busca (`ProductDiscoveryAgent`) só checava se as palavras batiam exatamente.
- A validação (`TrustAnalysisAgent`) usava um texto fixo ("Loja XYZ com score...").
- O ranqueamento (`RankingAgent`) só ordenava por ponto e preço usando matemática básica.

**A Meta:**
Injetar "cérebro" nesses agentes usando o **LangChain** para se conectar a um LLM local (Ollama). O objetivo era fazer com que eles raciocinassem sobre os dados, interpretassem as métricas e gerassem textos como se fossem consultores humanos, sem perder a base sólida que já estava construída.

---

## 🛠️ 2. Preparando a Infraestrutura (Dependências e Configurações)

### 2.1. Instalando o "Cérebro"
Primeiro, ensinamos o Python a falar com o Ollama instalando as bibliotecas do LangChain. No `requirements.txt`, adicionamos:
```text
langchain>=0.1.0
langchain-ollama>=0.2.0
langchain-community>=0.0.20
```

### 2.2. O Mapa para o Cérebro (.env e yaml)
Adicionamos no `.env.example` as portas de comunicação para o seu Ollama local:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b
```
E no arquivo `shopping_assistant/config/agent_configs.yaml`, dissemos explicitamente para os agentes usarem o `provider: "ollama"`.

### 2.3. O Cliente Singleton (`llm/client.py` e `llm/__init__.py`)
Criamos um arquivo que funciona como uma ponte central. A função `get_llm()` usa a técnica de *singleton* (carrega apenas uma vez na memória).
- **O que ele faz:** Tenta conectar no `http://localhost:11434`. Se a porta estiver aberta, ele retorna o "Cérebro" (`ChatOllama`).
- **Resiliência:** Se o Ollama estiver desligado (erro de conexão), ele não quebra o sistema. Ele avisa `[LLMClient] AVISO: Ollama indisponível` devolve `None` e o app volta a funcionar da forma antiga (determinística).

---

## 🗣️ 3. Dando Instruções (Prompts)

Para a IA saber o que fazer, criamos a pasta `config/prompts/` com instruções claras (os prompts). Pense nisso como o "escopo de trabalho" de um funcionário.

1.  **`discovery.txt`**: "Você é um Especialista em Busca. Leia estes JSONs, não invente produtos. Diga o que é relevante para '{query}'."
2.  **`trust_analysis.txt`**: "Você é o Analista de Lojas. Para a loja {store}, com as notas {reclame_aqui_rating}... Escreva um parágrafo que um humano comum entenderia sobre se a loja presta ou não."
3.  **`ranking.txt`**: "Você é um Consultor Final. Entre os itens aprovados para '{query}', escreva uma recomendação clara sugerindo qual o cliente deve comprar."

---

## 🧬 4. Conectando a IA aos Agentes (O Código)

### Agente 1: ProductDiscoveryAgent
*Antes:* Ele jogava a palavra na web, recebia a lista e ignorava palavras diferentes.
*Agora:* Ele faz as buscas do mesmo jeito, mas no final, se o `get_llm()` existir, ele injeta os 15 primeiros resultados no `discovery.txt` e pede pro Ollama raciocinar sobre eles. (Atualmente ele exibe esse raciocínio no console/terminal como enriquecimento textual).

### Agente 2: TrustAnalysisAgent
*Antes:* A propriedade `review_summary` era um texto preenchido de forma robotizada pelo validador.
*Agora:* Ele junta todas as métricas duras (Security, Reputation, Domain Match) e envia para o Ollama através do `trust_analysis.txt`.
**O Resultado:** O `review_summary` passa a ser um parecer gerado por IA ("A loja Casas Bahia é muito segura com 70 anos online, pode confiar...").

### Agente 3: RankingAgent
*Antes:* Apenas organizava a lista aprovada usando matemática `0.6 * Preço + 0.4 * Trust`.
*Agora:* Ele mantém a matemática (para ser justo) mas, no final, junta a lista e pede para o Ollama gerar uma RECOMENDAÇÃO ("Olha, a Amazon tem o melhor iPhone por R$ 6800..."). Essa recomendação é então injetada no início do resumo do "Top 1" Produto da lista.
*PS:* Para o RankingAgent funcionar, ensinamos o pai dele (`OrchestratorAgent`) a passar a `query` (a palavra que o cliente buscou) pra dentro dele como contexto.

---

## 💡 5. Como Estudar este Código?

Se você quiser ver a IA em ação:
1.  **Ligue seu Ollama** no terminal (`ollama run llama2:7b`).
2.  Inicie a busca (`python -m shopping_assistant.main "ps5"`).
3.  Vá acompanhando os logs:
    - Olhe o log `[LLMClient] Ollama conectado`.
    - Olhe os logs com a tag `[LLM]` informando o Raciocínio, a Análise de Loja e a Recomendação final.
4.  **Desligue o Ollama** e rode de novo:
    - O sistema detecta a falha e avisa que fará *Fallback* para o sistema matemático original perfeitamente.

## ✨ Resumo do Aprendizado
Nesta implementação foi utilizada a técnica de **Cadeia Aumentada por Ferramentas (Tool-Augmented/RAG approach)**. O LLM não pesquisa nada sozinho (pois ele alucina). O código Python (Scraper/SerpAPI/Matemática) gera os "Fatos Duros", e o LLM atua APENAS como "Intérprete/Redator" em cima das regras da sua Skill. É assim que se constrói IA robusta para produção!
