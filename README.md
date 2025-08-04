# The Nothing App - Chat System

A modular, agent-guided chat application built with FastAPI backend and React frontend.

## Quick Start

### Prerequisites

- Conda (miniconda or anaconda)
- Node.js and npm
- OpenRouter API key

### Easy Setup & Launch

1. **Clone and navigate to the project:**

   ```bash
   cd the-nothing-app/gob01-mini
   ```

2. **Set up your API key:**
   Create a `.env` file with your OpenRouter API key:

   ```bash
   echo "OPENROUTER_API_KEY=your_actual_api_key_here" > .env
   ```

3. **Launch the application:**

   **Option A: Using the bash script (recommended)**

   ```bash
   ./start.sh
   ```

   **Option B: Using the Python script**

   ```bash
   python start.py
   ```

4. **Access the application:**
   - **Chat Interface**: http://localhost:5173
   - **Backend API**: http://localhost:8001
   - **API Documentation**: http://localhost:8001/docs

## Manual Setup (if needed)

### Backend Setup

```bash
# Create conda environment (if not exists)
conda env create -f environment.yml

# Activate environment
conda activate agentic-framework

# Start backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## Architecture

- **Backend**: FastAPI with agent orchestration system
- **Frontend**: React with Vite and Tailwind CSS
- **Agents**: Modular agent system with coding and general assistants
- **Memory**: Session-based chat memory
- **Environment**: Conda-managed Python environment

## Agent System

The application uses a simplified agent architecture:

- **Main Agent**: Primary orchestrator that routes messages to specialized agents
- **Developer Persona**: Handles programming and technical queries (low temperature for precision)
- **Creative Persona**: Handles creative writing and brainstorming (high temperature for creativity)
- **Universal Agents**: Utility, web browsing, and embedding agents available to all personas
- **Automatic Fallback**: Free models for each agent type when primary models fail

## Configuration

The application uses a comprehensive configuration system via `config.yaml` in the root directory.

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key for LLM access

### Model Configuration

You can easily customize which models are used for different agents:

```yaml
models:
  # Main agent (primary orchestrator)
  main:
    model: "openai/gpt-4"
    temperature: 0.7
    max_tokens: 1500

  # Alternate personas
  personas:
    developer: # Software engineering
      model: "openai/gpt-4"
      temperature: 0.2
    creative: # Creative writing
      model: "openai/gpt-4"
      temperature: 0.8

  # Universal agents
  universal:
    utility: # Fast utility tasks
      model: "openai/gpt-3.5-turbo"
    web_browser: # Web browsing
      model: "openai/gpt-4"
    embedding: # Text embedding
      model: "text-embedding-ada-002"

  # Fallback models (free)
  fallbacks:
    main_fallback:
      model: "meta-llama/llama-3.2-3b-instruct:free"
    utility_fallback:
      model: "meta-llama/llama-3.2-1b-instruct:free"
    # ... more fallbacks
```

### Fallback System

The system includes automatic fallback to free models when API credits are exhausted:

- **Automatic Detection**: Detects payment/credit errors and switches to free models
- **Configurable Fallbacks**: Different fallback models for different agent types
- **Graceful Degradation**: System continues working even when primary models fail
- **User Notification**: Optionally notifies users when using fallback models

### Ports

- Frontend: 5173
- Backend: 8001

## Usage

1. Open the chat interface at http://localhost:5173
2. Type your message and press Enter or click Send
3. The system will automatically route your message to the most appropriate agent
4. View agent confidence scores and routing information in the terminal-style interface

## API Endpoints

### Chat API

- `POST /api/chat` - Main chat endpoint
- `GET /api/agents` - List available agents and capabilities

### Fallback Management

- `GET /api/fallback/status` - Check current fallback status for all agents
- `POST /api/fallback/reset` - Reset all agents to primary models
- `POST /api/fallback/force` - Force all agents to use fallback models

Example fallback status response:

```json
{
  "total_agents": 3,
  "agents_using_fallback": 1,
  "agents_status": {
    "general_assistant": {
      "using_fallback": true,
      "fallback_reason": "credit_exhausted",
      "primary_model": "openai/gpt-3.5-turbo",
      "fallback_model": "meta-llama/llama-3.2-3b-instruct:free"
    }
  }
}
```

## Stopping the Application

Press `Ctrl+C` in the terminal where you started the application. Both frontend and backend servers will be stopped gracefully.

## Troubleshooting

### Common Issues

1. **"Conda environment not found"**

   - Run: `conda env create -f environment.yml`

2. **"OpenRouter API key not configured"**

   - Check your `.env` file has the correct API key
   - Ensure the key starts with `sk-or-v1-`

3. **"Port already in use"**

   - Kill existing processes on ports 8001 or 5173
   - Or modify the ports in the startup scripts

4. **Frontend dependencies missing**
   - Run: `cd frontend && npm install`

### Logs

- Backend logs appear in the terminal where you started the application
- Frontend logs appear in the browser console (F12)

## Project Structure

```
the-nothing-app/gob01-mini/
├── backend/
│   ├── agents/          # Agent system
│   ├── assistants/      # Specialized assistants
│   ├── config/          # Configuration
│   ├── memory/          # Memory management
│   └── main.py          # FastAPI application
├── frontend/
│   ├── src/             # React source code
│   └── ChatTerminal.jsx # Main chat component
├── docs/                # Documentation
├── environment.yml      # Conda environment
├── start.sh            # Bash startup script
├── start.py            # Python startup script
└── .env                # Environment variables
```
