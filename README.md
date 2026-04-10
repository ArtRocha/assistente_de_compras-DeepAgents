# 🛍️ Assistente de Compras com Agentes de IA

Este projeto é um sistema completo e orquestrado para buscar, analisar e ranquear os melhores produtos. Ele utiliza a arquitetura de múltiplos agentes trabalhando em conjunto (Discovery, Trust e Ranking) equipados com **Inteligência Artificial local (Ollama)** para interpretação semântica dos dados da web.

## 🚀 Funcionalidades

- **Agentes com IA Real (Langchain + Ollama)**: O sistema não apenas executa lógicas de matemática e scraping, mas o LLM lê, interpreta e escreve relatórios e análises fáceis e humanizadas.
- **Orquestração de Processos**: Fluxo estruturado em módulos robustos que não travam caso a IA caia (Fallback determinístico automático).
- **Validação Inteligente da Loja**: Além de calcular reputação por algoritmos, elabora uma explicação clara em linguagem natural apontando riscos.
- **Busca via SerpAPI**: Conexão oficial com o Google Shopping para extração de ofertas reais com alta disponibilidade.
- **Frontend Interativo**: Uma interface visual (React/Vite) para ver e usar todo o poder do backend orquestrado.

---

## 🛠️ Instalação Simples e Rápida

Requisitos para rodar a aplicação:
- **Python 3.11** ou superior
- **Node.js**
- **Ollama** (Opcional, porém recomendado para rodar a IA)

### Passo 1: Clone o projeto

```bash
git clone <url-do-repositorio>
cd assistente_de_compras-DeepAgents
```

### Passo 2: Configure o Motor de IA Local (Ollama)

Se você desejar que os agentes pensem por si (Inteligência Artificial ligada), baixe e instale o **Ollama** gratuitamente através do site oficial: [ollama.com](https://ollama.com).

Após instalar, abra o seu terminal/cmd e baixe o modelo sugerido (o processo demorará um pouquinho pois um modelo de IA é pesado):
```bash
ollama pull llama2:7b
```
Você deve **deixar o aplicativo do Ollama aberto e rodando no seu computador** para que os Agentes de Código consigam conversar com ele.

*(Nota: Caso você não queira iniciar o Ollama, o sistema possui **fallback de segurança** e continuará operando normalmente na base da lógica determinística/matemática, retornando os produtos mesmo sem IA.)*

### Passo 3: Configure o Backend (Python)
1. Crie seu ambiente virtual isolado:
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Linux/MacOS:
   source venv/bin/activate
   ```
2. Instale os pacotes e dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie suas Variáveis de Ambiente locais:
   Copie o modelo de exemplo fornecido:
   ```bash
   cp .env.example .env
   ```
   **Importante:** Abra o arquivo `.env` e coloque a sua chave do **SerpAPI** (você obtém gratuitamente em [serpapi.com](https://serpapi.com)). Sem essa chave o sistema não fará as pesquisas na internet!

### Passo 4: Configure o Frontend (Node.js)
1. Ative a interface instalando suas bibliotecas:
   ```bash
   cd frontend
   npm install
   ```
   *Depois retorne a raiz principal via `cd ..`.*

---

## 📖 Como Inicializar o Projeto (Utilização)

O sistema exige duas janelas de terminal ativas simultaneamente: o cérebro/servidor e a "cara" visual.

### 1. Ligando o Servidor (Backend)
No terminal que está apontado na raiz principal do projeto com o `venv` ativado:
```bash
python shopping_assistant/api.py
```
> O backend iniciará em **http://localhost:8000** e já se conectará automaticamente na internet (SerpAPI) e na IA (Ollama).

*(Se preferir testar em terminal sem interface visual, execute o atalho: `python -m shopping_assistant.main "Iphone 15"`).*

### 2. Ligando a Interface Visual (Frontend)
Abra um novo terminal paralelo, acesse a pasta do frontend e inicie a navegação de tela:
```bash
cd frontend
npm run dev
```
> O site será aberto em **http://localhost:5173**. Basta clicar para acessar e conversar com os Agentes através da barra de pesquisa.

---

## 📚 Estude a Arquitetura

Acabamos de publicar um arquivo novo na raiz chamado `STUDY.md`. Ele explica didaticamente como pegamos as regras fixas de computação e injetamos Langchain e o Ollama por cima. Não deixe de ler se você quer entender *Como Montar Agentes Reais*.

- `shopping_assistant/agents/`: Onde cada agente LLM toma as decisões.
- `shopping_assistant/config/prompts/`: Onde estão as "ordens humanas" dadas pro cérebro da IA agir.
