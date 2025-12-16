# Technical Specifications

## Tech Stack
- **Language**: Python 3.10+
- **Framework**: Model Context Protocol (MCP) SDK (`mcp[cli]`)
- **Core Database**: `chromadb`
- **Package Management**: `uv` (implied by `uv.lock`), `hatchling` (build backend)
- **Testing**: `pytest`, `pytest-asyncio`, `pytest-cov`
- **Linting/Formatting**: `ruff`

## Dependencies
- **Core**:
    - `chromadb`: The vector database client/server.
    - `mcp`: Implementation of the Model Context Protocol.
    - `python-dotenv`: Environment variable management.
    - `httpx`: HTTP client for API requests.
- **Embedding Integration**:
    - `openai`, `cohere`, `voyageai`: Provider SDKs for generating embeddings.

## Development Setup
- **Environment**: Managed via `.env` file (loaded by `python-dotenv`).
- **Build**: Docker support via `Dockerfile`.
- **Configuration**:
    - `pyproject.toml`: Project metadata and dependencies.
    - `smithery.yaml`: Smithery configuration for MCP server registry.

## Technical Constraints
- **Client Types**: The server must support four distinct connection modes (Ephemeral, Persistent, HTTP, Cloud), necessitating flexible client initialization logic.
- **Embedding Persistence**: Relies on Chroma's collection configuration to persist embedding function settings.
- **Sync/Async**: FastMCP supports async tool definitions, which are used throughout `server.py` to ensure non-blocking operations where possible (though Chroma's python client is primarily synchronous, wrapping it in async functions is standard for MCP).

## Configuration Variables
### Connection
- `CHROMA_CLIENT_TYPE`: 'http', 'cloud', 'persistent', 'ephemeral'
- `CHROMA_HOST`: Hostname for HTTP client
- `CHROMA_PORT`: Port for HTTP client
- `CHROMA_SSL`: 'true'/'false' for HTTP client (default: true)

### OpenAI / Custom Embedding
- `CHROMA_OPENAI_API_KEY`: API Key for OpenAI or compatible provider.
- `CHROMA_OPENAI_API_BASE`: Base URL for API (e.g. for local LLMs).
- `CHROMA_OPENAI_MODEL_NAME`: Model name to use for embeddings.