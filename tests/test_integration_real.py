import pytest
import os
import json
import asyncio
import sys
from chroma_mcp.server import mcp, get_chroma_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if required environment variables are set for integration testing
CHROMA_HOST = os.getenv("CHROMA_HOST", "192.168.0.104")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8012")
CHROMA_OPENAI_API_KEY = os.getenv("CHROMA_OPENAI_API_KEY")

# Skip all tests in this module if not running integration tests or missing config
pytestmark = pytest.mark.integration

def is_integration_ready():
    """Check if the environment is ready for integration tests."""
    return bool(CHROMA_HOST and CHROMA_PORT and CHROMA_OPENAI_API_KEY)

@pytest.fixture(scope="module", autouse=True)
def setup_integration_env():
    """Setup environment variables and sys.argv for the MCP server to use during tests."""
    if not is_integration_ready():
        pytest.skip("Integration test environment variables not set")
    
    # Backup original environment and sys.argv
    original_env = os.environ.copy()
    original_argv = sys.argv.copy()
    
    # Set environment variables for the server
    os.environ["CHROMA_CLIENT_TYPE"] = "http"
    os.environ["CHROMA_HOST"] = CHROMA_HOST
    os.environ["CHROMA_PORT"] = CHROMA_PORT
    os.environ["CHROMA_SSL"] = "false"
    
    # Ensure embedding configuration is present
    if os.getenv("CHROMA_OPENAI_API_BASE"):
         os.environ["CHROMA_OPENAI_API_BASE"] = os.getenv("CHROMA_OPENAI_API_BASE")
    if os.getenv("CHROMA_OPENAI_MODEL_NAME"):
         os.environ["CHROMA_OPENAI_MODEL_NAME"] = os.getenv("CHROMA_OPENAI_MODEL_NAME")
         
    # Patch sys.argv to avoid argparse error in server.py
    # We provide minimal valid arguments to satisfy the parser
    sys.argv = ["chroma-mcp", "--client-type", "http"]

    yield
    
    # Restore environment and sys.argv
    os.environ.clear()
    os.environ.update(original_env)
    sys.argv = original_argv

@pytest.mark.asyncio
async def test_real_embedding_generation():
    """Test generating embeddings using the real configured provider (Gemini)."""
    texts = ["这是一个测试句子。", "This is a test sentence."]
    
    # We explicitly use 'openai' which is mapped to Gemini via configuration in this setup
    result = await mcp.call_tool("chroma_embed_texts", {
        "texts": texts,
        "embedding_function_name": "openai" 
    })
    
    assert len(result) == 1
    data = json.loads(result[0].text)
    
    assert "embeddings" in data
    embeddings = data["embeddings"]
    assert len(embeddings) == 2
    
    # Verification of dimensions
    # Gemini usually uses 768 or 3072 depending on the model.
    # If using gemini-embedding-001, it might be 768. 
    # If using text-embedding-004, it might be 768.
    # Let's check if it's NOT the default 384 (which would imply Mock or all-MiniLM-L6-v2)
    dim = len(embeddings[0])
    print(f"Detected embedding dimension: {dim}")
    
    assert dim > 0
    # Ensure it's not the default mock dimension if we are expecting real embeddings
    # Note: If the user configured a model that actually returns 384, this assertion might need adjustment,
    # but for Gemini it's typically higher.
    assert dim != 384, f"Got 384 dimensions, which suggests Mock/Default embedding was used instead of Real API. Dim: {dim}"

@pytest.mark.asyncio
async def test_end_to_end_rag():
    """Test full RAG flow: Create Collection -> Add Docs (with real embeddings) -> Query -> Delete."""
    collection_name = "test_integration_rag_flow"
    
    try:
        # 1. Create Collection
        # Note: We don't specify embedding function here, relying on server default or auto-selection
        await mcp.call_tool("chroma_create_collection", {"collection_name": collection_name})
        
        # 2. Add Documents
        # Using real embeddings generated on the fly
        docs = ["Python is a programming language.", "Chroma is a vector database."]
        ids = ["id1", "id2"]
        metadatas = [{"type": "lang"}, {"type": "db"}]
        
        await mcp.call_tool("chroma_add_documents", {
            "collection_name": collection_name,
            "documents": docs,
            "ids": ids,
            "metadatas": metadatas
        })
        
        # 3. Query Documents
        # Query for "vector db" which should match "Chroma is a vector database."
        query_text = "vector db"
        query_result = await mcp.call_tool("chroma_query_documents", {
            "collection_name": collection_name,
            "query_texts": [query_text],
            "n_results": 1
        })
        
        result_data = json.loads(query_result[0].text)
        assert len(result_data["documents"][0]) >= 1
        retrieved_doc = result_data["documents"][0][0]
        
        print(f"Query: '{query_text}' -> Retrieved: '{retrieved_doc}'")
        
        # Semantic check: Should retrieve the Chroma doc, not the Python doc
        assert "Chroma" in retrieved_doc
        
    finally:
        # 4. Cleanup
        try:
            await mcp.call_tool("chroma_delete_collection", {"collection_name": collection_name})
        except Exception as e:
            print(f"Cleanup failed: {e}")
