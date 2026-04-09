# 🛍️ Assistente de Compras Orquestrado

Atualmente, este projeto opera como um motor de busca robusto e orquestrado para ofertas. Embora utilize uma arquitetura inspirada em multi-agentes, as decisões e análises são, por enquanto, baseadas em lógica determinística e automação de Web Scraping. A integração de Inteligência Artificial real (LLMs) para raciocínio e análise semântica faz parte do roadmap de desenvolvimento.

## 🚀 Funcionalidades Atuais

- **Orquestração de Processos**: Fluxo estruturado em módulos (Discovery, Trust, Ranking) que simulam o comportamento de agentes especializados.
- **Validação de Lojas via Lógica**: Avalia a reputação da loja usando algoritmos de validação de dados (taxas de resposta, tempo de domínio, etc).
- **Busca em Tempo Real via SerpAPI**: Conexão oficial com o Google Shopping para extração de ofertas reais sem bloqueios.
- **Frontend Interativo**: Interface para visualização consolidada das melhores ofertas encontradas.

## 🛠️ Roadmap (Próximos Passos)

- [ ] **Agentes de IA (LLMs)**: Substituir a lógica fixa por agentes baseados em LLM (GPT-4/local) para análise subjetiva de reviews e intenção do usuário.
- [ ] **Análise Semântica de Confiança**: Usar IA para ler e resumir feedbacks reais de usuários sobre as lojas.
- [ ] **Comparativo Inteligente**: Chatbot para tirar dúvidas específicas sobre as diferenças entre os produtos encontrados.

---

## 🛠️ Instalação Simples e Rápida

Para fazer o projeto rodar, certifique-se de ter instalado em sua máquina:
- **Python 3.11** ou superior
- **Node.js**

### Passo 1: Clone o projeto

Baixe o projeto e entre na sua pasta:
```bash
git clone <url-do-repositorio>
cd assistente_de_compras-DeepAgents
```

### Passo 2: Configure o Backend (Python)
1. Recomendamos usar um ambiente virtual para não misturar bibliotecas:
   ```bash
   python -m venv venv
   
   # Para ativar no Windows:
   venv\Scripts\activate
   
   # Para ativar no Linux / MacOS:
   source venv/bin/activate
   ```
2. Instale as bibliotecas necessárias listadas no projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie e preencha as suas **Variáveis de Ambiente**:
   Crie uma cópia do arquivo de configurações de exemplo (ou renomeie-o se preferir):
   ```bash
   cp .env.example .env
   ```
   Abra o arquivo recém-criado chamado `.env` e certifique-se de preencher a variável `SERPAPI_KEY`. Você obtém sua chave API gratuitamente acessando o site [serpapi.com](https://serpapi.com). Sem ela, o sistema não poderá pesquisar produtos no Google!

### Passo 3: Configure o Frontend (Opcional, com Node.js)
1. Navegue para a página que tem o visual do assistente (`frontend`):
   ```bash
   cd frontend
   npm install
   ```

---

## 📖 Como Inicializar o Projeto (Uso)

Você precisará de dois terminais abertos: um irá rodar toda a “inteligência e pesquisa” (Backend) e o outro o site visual para conversarmos com os agentes (Frontend).

### 1. Iniciando o Backend
Abra o primeiro terminal, dentro da raiz do projeto e com o ambiente (venv) ativo, execute o servidor da API:
```bash
python shopping_assistant/api.py
```
> O backend estará pronto e operando na porta local: **http://localhost:8000**

*Observação:* Para testamentos cruos via linha de comando terminal (sem web), rode `python -m shopping_assistant.main "Iphone 15"`.

### 2. Iniciando o Frontend (Interface)
Abra um segundo terminal, entre na pasta `frontend` e rode o comando:
```bash
cd frontend
npm run dev
```
> Ao terminar, ele dará um endereço como **http://localhost:5173**. Acesse-o no seu navegador para utilizar o projeto completo e ver os dados da API sendo consultados. O Frontend já se encarrega de falar com a porta 8000 sozinho.

---

## 🏗️ Estrutura do Projeto

- `shopping_assistant/agents/`: Lógica central de raciocínio de cada agente (Orquestrador, Discovery, Ranking, Trust).
- `shopping_assistant/tools/`: Integrações web (SerpAPI, Validador de Lojas).
- `shopping_assistant/schemas/`: Modelos dos dados recebidos via Pydantic (`Product`, etc).
- `frontend/`: Interface contruída com ReactJS/Vite.
