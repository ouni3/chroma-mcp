# Product Documentation

## Purpose
The Chroma MCP Server bridges the gap between Large Language Models (LLMs) and Vector Databases. It allows AI assistants (like Claude or IDE agents) to persist data, manage knowledge bases, and retrieve relevant context using semantic search, effectively giving the AI "memory".

## Core Features
- **Flexible Connectivity**: Supports Ephemeral (in-memory), Persistent (local disk), HTTP (self-hosted), and Cloud (Chroma Cloud) connections.
- **Collection Management**: Full CRUD operations for vector collections (Create, Read, Update, Delete, List).
- **Document Operations**: 
    - **Add/Update**: Store text data with automatic or custom embeddings.
    - **Query**: Semantic search using vector similarity.
    - **Get**: Retrieve documents by ID or metadata filters.
    - **Delete**: Remove specific documents.
- **Analysis Tools**:
    - `chroma_generate_keywords`: Automatically generates representative keywords for a collection using vector clustering (K-Means) and hybrid text analysis (TextRank + TF-IDF) for maximum coverage.
- **Standalone Embedding**:
    - `chroma_embed_texts`: Generate embeddings for text lists without storing them, useful for intermediate vector operations.
- **Embedding Support**: 
    - Integrated with multiple providers (OpenAI, Cohere, VoyageAI, etc.) via Chroma's embedding functions.
    - **Custom OpenAI Configuration**: Supports connecting to any OpenAI-compatible embedding service (e.g., local LLMs, vLLM, Ollama) by configuring API Base and Model Name.

## User Experience Goals
- **Seamless Integration**: Works out-of-the-box with MCP-compliant clients (Claude Desktop, VS Code extensions).
- **Simplicity**: Abstract away the complexities of vector database management through simple tool calls.
- **Versatility**: Suitable for both local testing (ephemeral/persistent) and production deployment (HTTP/Cloud). Verified capabilities for remote Docker deployment.