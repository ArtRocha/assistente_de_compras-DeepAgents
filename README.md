# 🛍️ Multi-Agent Shopping Assistant

This project is a production-grade multi-agent system built using **LangChain DeepAgents** to search, analyze, and rank products across multiple stores.

## 🚀 Features

- **Multi-Agent Orchestration**: Specialized agents for discovery, trust analysis, and ranking.
- **Store Trust Evaluation**: Mock integration with "Reclame Aqui" data.
- **Advanced Scoring**: Combines price and trust into a final weighted score.
- **Async Support**: Parallel product search and trust data retrieval.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd agente_assistente_compras
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set PYTHONPATH**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   ```

## 📖 Usage

### Running the Backend API

1. Set your PYTHONPATH:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   ```

2. Start the FastAPI server (runs on port 8000):
   ```bash
   python -m uvicorn shopping_assistant.api:app --reload
   ```

### Running the Frontend UI

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Start the Vite development server (runs on port 5173 by default):
   ```bash
   npm run dev
   ```

The frontend will automatically proxy `/api` requests to the backend server.

## 🏗️ Project Structure

- `shopping_assistant/agents/`: Core agent logic.
- `shopping_assistant/tools/`: Integration with external services (mocked).
- `shopping_assistant/services/`: Data processing and scoring.
- `shopping_assistant/schemas/`: Pydantic data models.
- `shopping_assistant/config/`: Prompts and agent configurations.
