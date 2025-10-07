# Genkit Agent

AI Agent built with Google Genkit and Gemini integration for advanced conversational AI capabilities.

## Features

- 🤖 **Gemini Integration**: Powered by Google's Gemini 1.5 Flash model
- 🔧 **Genkit Framework**: Built on Google's Genkit AI framework
- 💬 **Conversation Memory**: Maintains conversation history
- 🌐 **REST API**: FastAPI-based HTTP endpoints
- 🎯 **Interactive Mode**: Command-line chat interface
- ⚙️ **Configurable**: Environment-based configuration

## Prerequisites

- Python 3.10 or higher
- Google AI API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))
- UV package manager (install from [astral.sh/uv](https://astral.sh/uv))

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/genkit-agent
   ```

2. **Install dependencies using UV:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google AI API key:
   ```env
   GOOGLE_AI_API_KEY=your_actual_api_key_here
   ```

## Usage

### Command Line Interface

**Basic demo:**
```bash
uv run python main.py
```

**Interactive chat mode:**
```bash
uv run python main.py interactive
```

### REST API Server

**Start the server:**
```bash
uv run python -m genkit_agent.server
```

The API will be available at `http://localhost:8000`

**API Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat` - Chat with the agent
- `GET /agent/info` - Get agent information
- `GET /agent/history` - Get conversation history
- `POST /agent/clear-history` - Clear conversation history

**Example API usage:**
```bash
# Chat with the agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello! How are you?"}'

# Get agent info
curl "http://localhost:8000/agent/info"
```

### Python API

```python
import asyncio
from genkit_agent import GenkitAgent

async def main():
    # Initialize the agent
    agent = GenkitAgent()
    
    # Chat with the agent
    response = await agent.chat("Hello! Can you help me?")
    print(response)
    
    # Get conversation history
    history = agent.get_conversation_history()
    print(f"Messages: {len(history)}")

# Run the async function
asyncio.run(main())
```

## Configuration

The agent can be configured through environment variables or the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_AI_API_KEY` | *Required* | Google AI API key |
| `AGENT_NAME` | `GenkitAgent` | Name of the agent |
| `MODEL_NAME` | `gemini-1.5-flash` | Gemini model to use |
| `HOST` | `localhost` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |

## Project Structure

```
genkit-agent/
├── genkit_agent/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── agent.py           # Core agent logic
│   ├── config.py          # Configuration management
│   └── server.py          # FastAPI server
├── main.py                # CLI entry point
├── pyproject.toml         # Project configuration
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Development

**Install development dependencies:**
```bash
uv sync --dev
```

**Code formatting:**
```bash
uv run black genkit_agent/
uv run isort genkit_agent/
```

**Type checking:**
```bash
uv run mypy genkit_agent/
```

**Run tests:**
```bash
uv run pytest
```

## Troubleshooting

**Common Issues:**

1. **API Key Error**: Make sure your `GOOGLE_AI_API_KEY` is set correctly in the `.env` file
2. **Import Error**: Ensure all dependencies are installed with `uv sync`
3. **Connection Error**: Check your internet connection for API calls to Google AI

**Getting Help:**

- Check the [Genkit documentation](https://firebase.google.com/docs/genkit)
- Review [Google AI documentation](https://ai.google.dev/)
- Ensure your API key has the necessary permissions

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

Built with ❤️ using [Google Genkit](https://firebase.google.com/docs/genkit) and [Gemini AI](https://ai.google.dev/)